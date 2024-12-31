import redis
from config import Config


class RedisCache:
    def __init__(self):
        self.redis_client = redis.StrictRedis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=Config.REDIS_DB,
            decode_responses=True,
        )

    def get_cached_price(self, title: str) -> float:
        """Retrieve the cached price for a given product title."""
        price = self.redis_client.get(title)
        return float(price) if price else None

    def set_cached_price(self, title: str, price: float):
        """Store the price of a product in the cache."""
        self.redis_client.set(title, price)
