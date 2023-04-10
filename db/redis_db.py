import redis



import redis


class RedisCache:

    def __init__(self) -> None:
        self.storage = redis.Redis(
            host='127.0.0.1',
            port=6379,
            encoding='utf-8', 
            retry_on_timeout=True,
            )

    def set_single(self, key: str, value: str) -> None:
        if not isinstance(value, (str, int)):
            raise TypeError(f'value variable must be str or int, not {type(value).__name__}')
        self.storage.set(name=key, value=value)

    def get_single(self, key: str) -> bool | str:
        value = self.storage.get(key)
        if value:
            return value.decode(encoding='utf-8')

        return False

    def delete(self, key: str):
        self.storage.delete(key)
    
redis = RedisCache()