from redis import Redis
from config import settings

try:
    print("REDIS_URI", settings.REDIS_URI)
    redis_client = Redis.from_url(settings.REDIS_URI)
except Exception as e:
    print(f"Error connecting to Redis: {e}")
    redis_client = None


def get_redis_client():
    return redis_client
