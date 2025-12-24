import os
from typing import Optional

from fastapi import (
    FastAPI,
    Query,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    Body,
)
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

from database import init_db, get_db
from models import SocialMediaPost, SentimentAnalysis, SentimentAlert
from websocket import ConnectionManager

# ─────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────
app = FastAPI(title="Sentiment Intelligence Platform")

manager = ConnectionManager()

# ─────────────────────────────────────────────
# ✅ CORS (THIS FIXES 80% OF YOUR ERRORS)
# ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# STARTUP
# ─────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    await init_db()

# ─────────────────────────────────────────────
# HEALTH
# ─────────────────────────────────────────────
@app.get("/api/health")
async def health():
    async for db in get_db():
        await db.execute(text("SELECT 1"))
    return {"status": "healthy"}

# ─────────────────────────────────────────────
# POSTS
# ─────────────────────────────────────────────
@app.get("/api/posts")
async def get_posts(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(
            SocialMediaPost.post_id,
            SocialMediaPost.content,
            SentimentAnalysis.sentiment_label,
            SentimentAnalysis.emotion,
        )
        .join(SentimentAnalysis, SocialMediaPost.post_id == SentimentAnalysis.post_id)
        .order_by(SocialMediaPost.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(query)
    rows = result.all()

    return [
        {
            "post_id": r[0],
            "content": r[1],
            "sentiment": r[2],
            "emotion": r[3],
        }
        for r in rows
    ]

# ─────────────────────────────────────────────
# ALERTS
# ─────────────────────────────────────────────
@app.get("/api/alerts")
async def get_alerts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SentimentAlert).order_by(SentimentAlert.id.desc()).limit(10)
    )
    return result.scalars().all()

# ─────────────────────────────────────────────
# SENTIMENT DISTRIBUTION
# ─────────────────────────────────────────────
@app.get("/api/sentiment/distribution")
async def sentiment_distribution(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            SentimentAnalysis.sentiment_label,
            func.count()
        ).group_by(SentimentAnalysis.sentiment_label)
    )
    return {row[0]: row[1] for row in result.all()}

# ─────────────────────────────────────────────
# 🔥 WEBSOCKET (STEP-8)
# ─────────────────────────────────────────────
@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ─────────────────────────────────────────────
# 🔥 INTERNAL BROADCAST (WORKER → BACKEND)
# ─────────────────────────────────────────────
@app.post("/internal/broadcast")
async def broadcast_event(payload: dict = Body(...)):
    await manager.broadcast(payload)
    return {"status": "ok"}

# ─────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )
