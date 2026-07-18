import redis
from app.core.config import settings

# Create a Redis connection pool
redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True # Automatically decodes byte responses to strings
)
