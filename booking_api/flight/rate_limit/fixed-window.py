import redis
from datetime import timedelta


def is_rate_limited(r, key, limit, period):
	#print(r.connection_pool.connection_kwargs)

	#print(limit)
	#print(period.total_seconds())
	try:
		#print(f"Before setnx: {r.get(key)}")
		if r.setnx(key, limit):
		#	print("setting r using setnx")
			r.expire(key, int(period.total_seconds()))
		#print(f"After setnx: {r.get(key)}")

	except Exception as e:
			print(f"Error setting key: {e}")
			
	bucket_val = r.get(key)
	if bucket_val and int(bucket_val) > 0:
		r.decrby(key, 1)
		return False
	
	return True
