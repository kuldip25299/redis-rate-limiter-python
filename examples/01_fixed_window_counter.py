"""
Fixed Window Counter Rate Limiter using Redis

Business Rule:
--------------
Allow a maximum of 5 requests per user every 60 seconds.

Redis Commands Used:
--------------------
INCR
EXPIRE
TTL

Requirements:
-------------
pip install redis

Start Redis:
------------
redis-server

Run:
----
python examples/01_fixed_window_counter.py
"""

import time
import redis

# ----------------------------------------------------
# Configuration
# ----------------------------------------------------

REDIS_HOST = "localhost"
REDIS_PORT = 6379

REQUEST_LIMIT = 5
WINDOW_SECONDS = 60

# ----------------------------------------------------
# Connect to Redis
# ----------------------------------------------------

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)

# ----------------------------------------------------
# Rate Limiter Function
# ----------------------------------------------------

def allow_request(user_id: str) -> bool:
    """
    Returns True if the request is allowed.
    Returns False if the user exceeded the limit.
    """

    key = f"rate_limit:user:{user_id}"

    # Increment request counter
    current_count = redis_client.incr(key)

    # First request?
    # Set expiration only once.
    if current_count == 1:
        redis_client.expire(key, WINDOW_SECONDS)

    ttl = redis_client.ttl(key)

    print("------------------------------------------")
    print(f"User ID        : {user_id}")
    print(f"Current Count  : {current_count}")
    print(f"Time Remaining : {ttl} seconds")

    if current_count <= REQUEST_LIMIT:
        print("Status         : ✅ Allowed")
        return True

    print("Status         : ❌ Blocked")
    return False


# ----------------------------------------------------
# Cleanup
# ----------------------------------------------------

def reset_user(user_id: str):
    """
    Remove user's rate limit key.
    Useful for demo purposes.
    """

    key = f"rate_limit:user:{user_id}"
    redis_client.delete(key)


# ----------------------------------------------------
# Demo
# ----------------------------------------------------

def main():

    user = "101"

    print("=" * 50)
    print(" Fixed Window Counter Demo ")
    print("=" * 50)

    reset_user(user)

    print()
    print(f"Limit : {REQUEST_LIMIT} requests every {WINDOW_SECONDS} seconds")
    print()

    for request in range(1, 8):

        print(f"\nRequest {request}")

        allow_request(user)

        time.sleep(1)

    print("\n" + "=" * 50)
    print("Waiting for the window to expire...")
    print("=" * 50)

    time.sleep(WINDOW_SECONDS)

    print("\nSending another request...\n")

    allow_request(user)


if __name__ == "__main__":
    main()
