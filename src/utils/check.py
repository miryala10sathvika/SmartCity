import redis

# Connect to Redis
try:
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
    redis_client.ping()  # Check if Redis server is reachable
    print("Connected to Redis successfully")
except redis.ConnectionError as e:
    print(f"Redis connection error: {e}")

# Use redis_client in your Flask application
