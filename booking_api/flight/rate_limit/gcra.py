from datetime import timedelta
from redis import Redis


def is_rate_limited(r: Redis, key: str, limit: int, period: timedelta):
    period_in_seconds = int(period.total_seconds())
    t = r.time()[0]
    separation = round(period_in_seconds / limit)
    r.setnx(key, 0)
    tat = max(int(r.get(key)), t)
    if tat - t <= period_in_seconds - separation:
        new_tat = max(tat, t) + separation
        r.set(key, new_tat)
        return False
    return True