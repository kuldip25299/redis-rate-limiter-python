"""
Sliding Window Log Rate Limiter using Redis

Business Rule
-------------
Allow a maximum of 5 requests within any rolling
60-second window.

Redis Data Structure
--------------------
Sorted Set (ZSET)

Redis Commands Used
-------------------
ZADD
ZREMRANGEBYSCORE
ZCARD
ZRANGE
EXPIRE

Requirements
------------
pip install redis

Start Redis
-----------
redis-server

Run
---
python examples/02_sliding_window_log.py
"""

import time
from datetime import datetime

import redis

# ==========================================================
# Configuration
# ==========================================================

REDIS_HOST = "localhost"
REDIS_PORT = 6379

REQUEST_LIMIT = 5
WINDOW_SIZE = 60

# ==========================================================
# Redis Connection
# ==========================================================

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
)

# ==========================================================
# Helper Functions
# ==========================================================


def redis_key(user_id: str) -> str:
    return f"rate_limit:user:{user_id}"


def print_line():
    print("-" * 65)


def print_title(title: str):
    print("\n" + "=" * 65)
    print(title)
    print("=" * 65)


def print_sorted_set(key: str):
    """
    Display current Redis Sorted Set.
    """

    members = redis_client.zrange(key, 0, -1, withscores=True)

    print("\nRedis Sorted Set")

    if not members:
        print("(empty)")
        return

    print_line()

    for member, score in members:
        ts = datetime.fromtimestamp(score)
        print(f"{member:<15} {ts.strftime('%H:%M:%S')}")


# ==========================================================
# Sliding Window Algorithm
# ==========================================================


def allow_request(user_id: str) -> bool:
    """
    Returns True if request is allowed.
    Returns False otherwise.
    """

    key = redis_key(user_id)

    current_time = time.time()

    window_start = current_time - WINDOW_SIZE

    request_id = f"req-{int(current_time)}"

    print("\nCurrent Time")

    print(
        datetime.fromtimestamp(current_time).strftime(
            "%H:%M:%S"
        )
    )

    print("\nStep 1 : Remove expired requests")

    removed = redis_client.zremrangebyscore(
        key,
        0,
        window_start,
    )

    print(f"Removed : {removed}")

    print("\nStep 2 : Count requests in current window")

    current_count = redis_client.zcard(key)

    print(f"Current Count : {current_count}")

    if current_count >= REQUEST_LIMIT:

        ttl = redis_client.ttl(key)

        print("\nDecision")

        print("❌ Request Blocked")

        print(f"TTL : {ttl} seconds")

        return False

    print("\nStep 3 : Add current request")

    redis_client.zadd(
        key,
        {
            request_id: current_time
        },
    )

    redis_client.expire(
        key,
        WINDOW_SIZE,
    )

    print("\nDecision")

    print("✅ Request Allowed")

    print_sorted_set(key)

    return True


# ==========================================================
# Cleanup
# ==========================================================


def reset_user(user_id: str):
    redis_client.delete(redis_key(user_id))


# ==========================================================
# Demo
# ==========================================================


def main():

    user = "101"

    print_title("Sliding Window Log Rate Limiter Demo")

    print("Business Rule")
    print("--------------------------")
    print(f"Maximum Requests : {REQUEST_LIMIT}")
    print(f"Window           : {WINDOW_SIZE} Seconds")

    reset_user(user)

    print("\nSending Requests...\n")

    # ------------------------------------------------------
    # First Five Requests
    # ------------------------------------------------------

    for request in range(1, 6):

        print_line()

        print(f"Request {request}")

        allow_request(user)

        time.sleep(2)

    # ------------------------------------------------------
    # Sixth Request
    # ------------------------------------------------------

    print_line()

    print("Request 6")

    allow_request(user)

    # ------------------------------------------------------
    # Wait
    # ------------------------------------------------------

    print("\n")
    print("=" * 65)

    print("Waiting for oldest requests to expire...")

    print("=" * 65)

    time.sleep(55)

    print_line()

    print("Request After Window Slides")

    allow_request(user)

    print("\nFinal Redis State")

    print_sorted_set(redis_key(user))


if __name__ == "__main__":
    main()
