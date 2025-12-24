import os
import asyncio
import logging
from datetime import datetime, timezone, timedelta

import httpx
from dotenv import load_dotenv
from redis.asyncio import Redis
from redis.exceptions import ResponseError
from transformers import pipeline

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select, func

from models import SocialMediaPost, SentimentAnalysis, SentimentAlert

# ─────────────────────────────────────────────
# ENV + LOGGING
# ─────────────────────────────────────────────
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [WORKER] %(levelname)s - %(message)s"
)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
STREAM_NAME = os.getenv("REDIS_STREAM_NAME")
GROUP_NAME = os.getenv("REDIS_CONSUMER_GROUP")
CONSUMER_NAME = "worker-1"

DATABASE_URL = os.getenv("DATABASE_URL")
BACKEND_INTERNAL_URL = "http://backend:8000/internal/broadcast"

SENTIMENT_MODEL = os.getenv("HUGGINGFACE_MODEL")
EMOTION_MODEL = os.getenv("EMOTION_MODEL")

ALERT_THRESHOLD = float(os.getenv("ALERT_NEGATIVE_RATIO_THRESHOLD", 0.1))
ALERT_WINDOW = int(os.getenv("ALERT_WINDOW_MINUTES", 5))
ALERT_MIN_POSTS = int(os.getenv("ALERT_MIN_POSTS", 10))

# ─────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# ─────────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────────
sentiment_pipe = pipeline("sentiment-analysis", model=SENTIMENT_MODEL, device=-1)
emotion_pipe = pipeline("text-classification", model=EMOTION_MODEL, top_k=1, device=-1)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def parse_utc_naive(iso_ts: str):
    dt = datetime.fromisoformat(iso_ts)
    if dt.tzinfo:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt

def normalize_sentiment(label: str) -> str:
    label = label.lower()
    if "positive" in label:
        return "positive"
    if "negative" in label:
        return "negative"
    return "neutral"

async def notify_backend(payload: dict):
    async with httpx.AsyncClient(timeout=2.0) as client:
        await client.post(BACKEND_INTERNAL_URL, json=payload)

# ─────────────────────────────────────────────
# ALERT ENGINE
# ─────────────────────────────────────────────
async def evaluate_alerts(session: AsyncSession):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    window_start = now - timedelta(minutes=ALERT_WINDOW)

    query = (
        select(
            SentimentAnalysis.sentiment_label,
            func.count(SentimentAnalysis.id)
        )
        .where(SentimentAnalysis.analyzed_at >= window_start)
        .group_by(SentimentAnalysis.sentiment_label)
    )

    result = await session.execute(query)
    counts = dict(result.all())

    pos = counts.get("positive", 0)
    neg = counts.get("negative", 0)
    total = sum(counts.values())

    if total >= ALERT_MIN_POSTS and pos > 0:
        ratio = neg / pos
        if ratio >= ALERT_THRESHOLD:
            session.add(
                SentimentAlert(
                    alert_type="high_negative_ratio",
                    threshold_value=ALERT_THRESHOLD,
                    actual_value=ratio,
                    window_start=window_start,
                    window_end=now,
                    post_count=total,
                )
            )

            await notify_backend({
                "type": "alert",
                "ratio": ratio,
                "post_count": total,
                "window_start": window_start.isoformat(),
                "window_end": now.isoformat()
            })

# ─────────────────────────────────────────────
# MAIN PROCESS
# ─────────────────────────────────────────────
async def process_message(redis, message_id, data):
    async with SessionLocal() as session:
        async with session.begin():
            raw_sentiment = sentiment_pipe(data["content"])[0]
            emotion = emotion_pipe(data["content"])[0][0]

            sentiment_label = normalize_sentiment(raw_sentiment["label"])

            await session.execute(
                text("""
                INSERT INTO social_media_posts (post_id, source, content, author, created_at)
                VALUES (:post_id, :source, :content, :author, :created_at)
                ON CONFLICT (post_id) DO NOTHING
                """),
                {
                    "post_id": data["post_id"],
                    "source": data["source"],
                    "content": data["content"],
                    "author": data["author"],
                    "created_at": parse_utc_naive(data["created_at"])
                }
            )

            await session.execute(
                text("""
                INSERT INTO sentiment_analysis (post_id, model_name, sentiment_label, confidence_score, emotion)
                VALUES (:post_id, :model, :label, :score, :emotion)
                """),
                {
                    "post_id": data["post_id"],
                    "model": SENTIMENT_MODEL,
                    "label": sentiment_label,
                    "score": raw_sentiment["score"],
                    "emotion": emotion["label"]
                }
            )

            await notify_backend({
                "type": "sentiment",
                "post_id": data["post_id"],
                "sentiment": sentiment_label,
                "emotion": emotion["label"]
            })

            await evaluate_alerts(session)

    await redis.xack(STREAM_NAME, GROUP_NAME, message_id)

# ─────────────────────────────────────────────
# LOOP
# ─────────────────────────────────────────────
async def worker_loop():
    redis = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    try:
        await redis.xgroup_create(STREAM_NAME, GROUP_NAME, id="0", mkstream=True)
    except ResponseError:
        pass

    while True:
        messages = await redis.xreadgroup(
            GROUP_NAME,
            CONSUMER_NAME,
            {STREAM_NAME: ">"},
            count=1,
            block=5000
        )
        for _, entries in messages:
            for message_id, data in entries:
                await process_message(redis, message_id, data)

if __name__ == "__main__":
    asyncio.run(worker_loop())
