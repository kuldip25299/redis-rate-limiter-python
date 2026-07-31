"""
Sliding Window Counter Rate Limiter using Redis

Business Rule
-------------
Allow a maximum of 5 requests within a rolling
60-second window.

Unlike Sliding Window Log, this implementation
does NOT store every request timestamp.

Instead, it stores only two counters:

1. Previous Window Counter
2. Current Window Counter

The final request count is calculated using
a weighted average.

Redis Data Structure
--------------------
Hash

Redis Commands Used
-------------------
HSET
HGETALL
HINCRBY
EXPIRE

Python Version
--------------
Python 3.12+

Run
---
python examples/03_sliding_window_counter.py
"""

import math
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
    """
    Build Redis key.
    """
    return f"rate_limit:user:{user_id}"


def current_window(timestamp: float) -> int:
    """
    Returns the current window number.

    Example

    timestamp = 1714557605

    Window = 28575960
    """

    return math.floor(timestamp / WINDOW_SIZE)


def print_separator():
    print("-" * 70)


def print_header(title: str):

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


# ==========================================================
# Redis Inspection
# ==========================================================


def print_redis_state(key: str):

    data = redis_client.hgetall(key)

    print()
    print("Redis Hash")
    print_separator()

    if not data:
        print("(empty)")
        return

    for field, value in data.items():
        print(f"{field:<20}: {value}")


# ==========================================================
# Sliding Window Counter
# ==========================================================


def allow_request(user_id: str) -> bool:
    """
    Returns True if request is allowed.
    Returns False otherwise.
    """

    key = redis_key(user_id)

    now = time.time()

    window = current_window(now)

    elapsed = now % WINDOW_SIZE

    overlap = (WINDOW_SIZE - elapsed) / WINDOW_SIZE

    data = redis_client.hgetall(key)

    stored_window = int(data.get("window", -1))

    current_count = int(data.get("current_count", 0))

    previous_count = int(data.get("previous_count", 0))

    # ------------------------------------------------------
    # Window Changed?
    # ------------------------------------------------------

    if stored_window != window:

        previous_count = current_count
        current_count = 0

        redis_client.hset(
            key,
            mapping={
                "window": window,
                "previous_count": previous_count,
                "current_count": current_count,
            },
        )

    # ------------------------------------------------------
    # Weighted Count
    # ------------------------------------------------------

    estimated_count = (
        previous_count * overlap
    ) + current_count

    print()
    print("Current Time")
    print("--------------------------------")

    print(
        datetime.fromtimestamp(now).strftime(
            "%H:%M:%S"
        )
    )

    print()

    print(f"Current Window  : {window}")

    print(f"Current Counter : {current_count}")

    print(f"Previous Counter: {previous_count}")

    print(f"Window Overlap  : {overlap:.2f}")

    print()

    print(
        f"Estimated Count : "
        f"{previous_count} × {overlap:.2f}"
        f" + {current_count}"
        f" = {estimated_count:.2f}"
    )

    # ------------------------------------------------------
    # Decision
    # ------------------------------------------------------

    if estimated_count >= REQUEST_LIMIT:

        print()

        print("Decision")

        print("❌ Request Blocked")

        return False

    # ------------------------------------------------------
    # Increment Current Counter
    # ------------------------------------------------------

    current_count += 1

    redis_client.hset(
        key,
        "current_count",
        current_count,
    )

    redis_client.expire(
        key,
        WINDOW_SIZE * 2,
    )

    print()

    print("Decision")

    print("✅ Request Allowed")

    print()

    print_redis_state(key)

    return True

# ==========================================================
# Cleanup
# ==========================================================

def reset_user(user_id: str):
    """
    Remove the user's rate limiting data from Redis.

    This keeps every demo execution clean.
    """
    redis_client.delete(redis_key(user_id))


# ==========================================================
# Demo Functions
# ==========================================================

def print_business_rule():

    print_header("Sliding Window Counter Rate Limiter")

    print("Business Rule")
    print_separator()

    print(f"Maximum Requests : {REQUEST_LIMIT}")
    print(f"Window Size      : {WINDOW_SIZE} Seconds")

    print()
    print(
        "This implementation stores only two counters "
        "instead of every request timestamp."
    )


def simulate_requests():

    user = "101"

    print()
    print("User ID :", user)

    print()
    print("Starting request simulation...")

    # --------------------------------------------------
    # First Five Requests
    # --------------------------------------------------

    for request_number in range(1, 6):

        print()
        print_separator()

        print(f"Request {request_number}")

        allow_request(user)

        #
        # Wait a little so we can see the
        # overlap percentage changing.
        #
        time.sleep(5)

    # --------------------------------------------------
    # Sixth Request
    # --------------------------------------------------

    print()
    print_separator()

    print("Request 6")

    allow_request(user)

    # --------------------------------------------------
    # Wait
    # --------------------------------------------------

    print()
    print("=" * 70)
    print("Waiting for the sliding window to move forward...")
    print("=" * 70)

    #
    # After ~35 seconds, the overlap with the
    # previous window becomes much smaller.
    #
    time.sleep(35)

    print()
    print_separator()

    print("Request After Sliding Window")

    allow_request(user)


# ==========================================================
# Redis Explanation
# ==========================================================

def explain_redis_storage():

    print()
    print_header("What Redis Stores")

    print(
        """
Redis Hash

Key

rate_limit:user:101

Fields

window

previous_count

current_count

Unlike Sliding Window Log,
Redis does NOT store every request.

Regardless of whether the user sends

10 requests

or

10,000 requests,

only these counters are stored.
"""
    )


# ==========================================================
# Algorithm Explanation
# ==========================================================

def explain_algorithm():

    print()
    print_header("How Estimated Count Is Calculated")

    print(
        """
Estimated Count

=

Previous Counter × Window Overlap

+

Current Counter

Example

Previous Counter = 4

Current Counter = 2

Window Overlap = 0.40

Estimated Count

=

4 × 0.40

+

2

=

3.60

This approximation allows us to avoid
storing every request timestamp while still
producing a smooth rolling window.
"""
    )


# ==========================================================
# Main
# ==========================================================

def main():

    user = "101"

    reset_user(user)

    print_business_rule()

    explain_redis_storage()

    explain_algorithm()

    simulate_requests()

    print()

    print_header("Final Redis State")

    print_redis_state(redis_key(user))

    print()

    print_header("Demo Complete")

    print(
        """
Key Takeaways

✓ Only two counters are stored.

✓ Memory usage stays almost constant.

✓ No request timestamps are stored.

✓ More scalable than Sliding Window Log.

✓ Slightly less accurate because the
  request count is estimated.

Next Example

Token Bucket
"""
    )


# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":

    try:

        main()

    except redis.ConnectionError:

        print()

        print("Unable to connect to Redis.")

        print("Make sure Redis is running on localhost:6379")

    except KeyboardInterrupt:

        print()

        print("Program interrupted by user.")
