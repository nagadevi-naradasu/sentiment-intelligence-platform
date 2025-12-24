import os
import time
import random
import uuid
import logging
from datetime import datetime, timezone

from redis import Redis
from redis.exceptions import RedisError
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [INGESTER] %(levelname)s - %(message)s"
)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
STREAM_NAME = os.getenv("REDIS_STREAM_NAME", "social_posts_stream")

POSTS_PER_MINUTE = int(os.getenv("POSTS_PER_MINUTE", 60))
SLEEP_INTERVAL = 60 / POSTS_PER_MINUTE


class DataIngester:
    """
    Publishes simulated social media posts to Redis Stream
    """

    def __init__(self, redis_client: Redis, stream_name: str):
        self.redis = redis_client
        self.stream_name = stream_name

        self.positive_templates = [
            "I absolutely love {product}! It works amazingly well.",
            "{product} exceeded my expectations. Highly recommended!",
            "So happy with my experience using {product}.",
            "This is amazing! {product} just keeps getting better."
        ]

        self.negative_templates = [
            "Very disappointed with {product}. Not worth the money.",
            "Terrible experience using {product}.",
            "I hate how {product} performs. Completely useless.",
            "{product} is a big letdown. Would not recommend."
        ]

        self.neutral_templates = [
            "Just tried {product} today.",
            "Received {product} earlier this morning.",
            "Using {product} for the first time.",
            "I am currently testing {product}."
        ]

        self.products = [
            "iPhone 16",
            "Tesla Model 3",
            "ChatGPT",
            "Netflix",
            "Amazon Prime",
            "Google Pixel",
            "MacBook Pro"
        ]

        self.sources = ["twitter", "reddit", "linkedin"]

    def generate_post(self) -> dict:
        sentiment_bucket = random.choices(
            ["positive", "neutral", "negative"],
            weights=[40, 30, 30],
            k=1
        )[0]

        product = random.choice(self.products)

        if sentiment_bucket == "positive":
            content = random.choice(self.positive_templates)
        elif sentiment_bucket == "negative":
            content = random.choice(self.negative_templates)
        else:
            content = random.choice(self.neutral_templates)

        post = {
            "post_id": f"post_{uuid.uuid4().hex}",
            "source": random.choice(self.sources),
            "content": content.format(product=product),
            "author": f"user_{random.randint(1000, 9999)}",
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        return post

    def publish_post(self, post_data: dict) -> bool:
        try:
            self.redis.xadd(self.stream_name, post_data)
            logging.info(f"Published post {post_data['post_id']}")
            return True
        except RedisError as e:
            logging.error(f"Redis publish failed: {e}")
            return False

    def start(self):
        logging.info("Ingester started")
        logging.info(f"Publishing ~{POSTS_PER_MINUTE} posts/minute")

        while True:
            post = self.generate_post()
            self.publish_post(post)
            time.sleep(SLEEP_INTERVAL)


def create_redis_client() -> Redis:
    return Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True
    )


if __name__ == "__main__":
    redis_client = create_redis_client()
    ingester = DataIngester(redis_client, STREAM_NAME)
    ingester.start()
