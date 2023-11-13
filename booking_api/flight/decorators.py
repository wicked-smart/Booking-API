from flight.rate_limit.gcra import is_rate_limited
import redis
import os

redis_url = os.environ.get('REDIS_URL')
r =  redis.Redis.from_url(redis_url)

print(r)
def rate_limit(limit, period):
    def decorator(task):
        def wrapper(*args, **kwargs):
            key = f"key_{task.__name__}"
            print(key)

            if not is_rate_limited(r, key, limit, period):
                print("performing the task...")
                return task(*args)
            else:
                print("Task is Rate Limited!!!")
                return None
        return wrapper
    return decorator


