"""
Token Bucket Rate Limiter using Redis

Business Rule
-------------
Allow requests while tokens are available.

Each request consumes one token.

Tokens are automatically replenished over time.

Redis Data Structure
--------------------
Hash

Redis Commands Used
-------------------
HSET
HGETALL
EXPIRE

Python Version
--------------
Python 3.12+

Run
---
python examples/04_token_bucket.py
"""

import time
from datetime import datetime

import redis

# ==========================================================
# Configuration
# ==========================================================

REDIS_HOST = "localhost"
REDIS_PORT = 6379

# Maximum tokens the bucket can hold
BUCKET_CAPACITY = 5

# Number of tokens added every second
REFILL_RATE = 1

# Expire inactive buckets after this many seconds
KEY_EXPIRY = 300

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
    Generate Redis key.
    """
    return f"token_bucket:{user_id}"


def print_line():
    print("-" * 70)


def print_header(title: str):

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


# ==========================================================
# Bucket Visualization
# ==========================================================


def bucket_visual(tokens: float) -> str:
    """
    Convert token count into a visual bucket.

    Example

    5 -> ★★★★★

    3 -> ★★★☆☆

    1 -> ★☆☆☆☆
    """

    full = int(tokens)

    empty = BUCKET_CAPACITY - full

    return "★" * full + "☆" * empty


# ==========================================================
# Redis Inspection
# ==========================================================


def print_bucket_state(user_id: str):

    key = redis_key(user_id)

    data = redis_client.hgetall(key)

    print()
    print("Redis State")
    print_line()

    if not data:
        print("(empty)")
        return

    tokens = float(data["tokens"])

    refill = float(data["last_refill"])

    print(f"Redis Key     : {key}")
    print(f"Tokens        : {tokens:.2f}")
    print(f"Bucket        : {bucket_visual(tokens)}")
    print(
        "Last Refill   :",
        datetime.fromtimestamp(refill).strftime("%H:%M:%S"),
    )


# ==========================================================
# Token Bucket
# ==========================================================


def allow_request(user_id: str) -> bool:
    """
    Returns True if request is allowed.

    Returns False if bucket is empty.
    """

    key = redis_key(user_id)

    now = time.time()

    data = redis_client.hgetall(key)

    # ------------------------------------------------------
    # First Request
    # ------------------------------------------------------

    if not data:

        tokens = BUCKET_CAPACITY

        last_refill = now

    else:

        tokens = float(data["tokens"])

        last_refill = float(data["last_refill"])

    # ------------------------------------------------------
    # Calculate New Tokens
    # ------------------------------------------------------

    elapsed = now - last_refill

    tokens_to_add = int(elapsed * REFILL_RATE)
    
    if tokens_to_add > 0:
    
        tokens = min(
            BUCKET_CAPACITY,
            tokens + tokens_to_add,
        )
    
        last_refill = now

    print()
    print("Current Time")
    print("--------------------------------")

    print(
        datetime.fromtimestamp(now).strftime(
            "%H:%M:%S"
        )
    )

    print()

    print(f"Elapsed Time      : {elapsed:.2f} seconds")

    print(f"Tokens Refilled   : {tokens_to_add:.2f}")

    print(f"Available Tokens  : {tokens:.2f}")

    print(f"Bucket            : {bucket_visual(tokens)}")

    # ------------------------------------------------------
    # Check Bucket
    # ------------------------------------------------------

    if tokens < 1:

        redis_client.hset(
            key,
            mapping={
                "tokens": tokens,
                "last_refill": last_refill,
            },
        )

        redis_client.expire(
            key,
            KEY_EXPIRY,
        )

        print()

        print("Decision")

        print("❌ Request Blocked")

        print()

        print_bucket_state(user_id)

        return False

    # ------------------------------------------------------
    # Consume Token
    # ------------------------------------------------------

    tokens -= 1

    redis_client.hset(
        key,
        mapping={
            "tokens": tokens,
            "last_refill": last_refill,
        },
    )

    redis_client.expire(
        key,
        KEY_EXPIRY,
    )

    print()

    print("One token consumed.")

    print()

    print(f"Remaining Tokens : {tokens:.2f}")

    print(f"Bucket           : {bucket_visual(tokens)}")

    print()

    print("Decision")

    print("✅ Request Allowed")

    print_bucket_state(user_id)

    return True

# ==========================================================
# Cleanup
# ==========================================================


def reset_bucket(user_id: str):
    """
    Remove bucket from Redis.

    This allows every demo run to start
    with a fresh bucket.
    """

    redis_client.delete(redis_key(user_id))


# ==========================================================
# Demo Information
# ==========================================================


def print_business_rule():

    print_header("Token Bucket Rate Limiter")

    print("Business Rule")
    print_line()

    print(f"Bucket Capacity : {BUCKET_CAPACITY} Tokens")

    print(f"Refill Rate     : {REFILL_RATE} Token / Second")

    print()

    print(
        "Every request consumes one token.\n"
        "Tokens are automatically replenished over time."
    )


def explain_bucket():

    print_header("How Token Bucket Works")

    print(
        """
Imagine every user owns a bucket.

Each token inside the bucket represents permission
to make one request.

When a request arrives:

    Request
       │
       ▼
Consume One Token
       │
       ▼
Allow Request

If the bucket becomes empty:

    Request
       │
       ▼
No Tokens Available
       │
       ▼
Reject Request

The bucket automatically refills over time.

No cron job.

No scheduler.

No background process.

Tokens are calculated only when the next
request arrives.
"""
    )


# ==========================================================
# Demo Helpers
# ==========================================================


def wait_with_progress(seconds: int):
    """
    Wait while showing progress.

    This makes it easier to observe
    token refilling.
    """

    print()

    print(f"Waiting {seconds} seconds")

    for second in range(seconds):

        print(
            f"  {second + 1}/{seconds} sec",
            end="\r",
            flush=True,
        )

        time.sleep(1)

    print()


def send_request(user_id: str, request_number: int):

    print()
    print_line()

    print(f"Request #{request_number}")

    allow_request(user_id)


# ==========================================================
# Demo Simulation
# ==========================================================


def simulate_bucket(user_id: str):

    print_header("Starting Demo")

    print(
        """
Scenario

A user starts with a full bucket.

Five requests are sent immediately.

The sixth request should fail.

After waiting a few seconds,
tokens will automatically refill.

The next request should succeed.
"""
    )

    # --------------------------------------------
    # First Five Requests
    # --------------------------------------------

    for request in range(1, 6):

        send_request(
            user_id=user_id,
            request_number=request,
        )

        #
        # Short pause so the output
        # is easier to follow.
        #
        time.sleep(1)

    # --------------------------------------------
    # Sixth Request
    # --------------------------------------------

    send_request(
        user_id=user_id,
        request_number=6,
    )

    # --------------------------------------------
    # Wait
    # --------------------------------------------

    print()

    print("=" * 70)

    print("Bucket is empty.")

    print("Waiting for tokens to refill...")

    print("=" * 70)

    wait_with_progress(3)

    print()

    print("Checking bucket again...")

    send_request(
        user_id=user_id,
        request_number=7,
    )

    # --------------------------------------------
    # Wait Longer
    # --------------------------------------------

    print()

    print("=" * 70)

    print("Waiting longer to refill more tokens...")

    print("=" * 70)

    wait_with_progress(5)

    send_request(
        user_id=user_id,
        request_number=8,
    )


# ==========================================================
# Redis Storage Explanation
# ==========================================================


def explain_redis_storage():

    print_header("Redis Storage")

    print(
        """
Redis stores only two values.

Hash

token_bucket:<user_id>

-----------------------------------

tokens

last_refill

-----------------------------------

Unlike Sliding Window Log,

Redis does NOT store every request.

Memory usage remains constant,
regardless of request volume.
"""
    )


# ==========================================================
# Algorithm Summary
# ==========================================================


def explain_algorithm():

    print_header("Algorithm")

    print(
        """
Request Arrives

        │

        ▼

Read Bucket From Redis

        │

        ▼

Calculate Time Elapsed

        │

        ▼

Refill Tokens

        │

        ▼

Token Available?

      /     \\

    Yes      No

     │        │

Consume      Reject

Token
"""
    )


# ==========================================================
# Main
# ==========================================================


def main():

    user_id = "101"

    #
    # Always start with a fresh bucket
    #
    reset_bucket(user_id)

    print_business_rule()

    explain_bucket()

    explain_redis_storage()

    explain_algorithm()

    simulate_bucket(user_id)

    #
    # Display final Redis state
    #
    print()

    print_header("Final Redis State")

    print_bucket_state(user_id)

    #
    # Demo Summary
    #
    print()

    print_header("Summary")

    print(
        """
What Happened?

✓ User started with a full bucket.

✓ Every request consumed one token.

✓ Once the bucket became empty,
  additional requests were rejected.

✓ After waiting, tokens were
  automatically refilled.

✓ The next request was accepted.

Notice something important.

At no point did Redis run a scheduler,
background job or timer.

The refill happened only when the next
request arrived.

This lazy refill approach is one of the
reasons Token Bucket is efficient and
widely used in production systems.
"""
    )

    #
    # Final Notes
    #
    print()

    print_header("Key Takeaways")

    print(
        f"""
Bucket Capacity : {BUCKET_CAPACITY}

Refill Rate     : {REFILL_RATE} Token / Second

Redis Storage

• tokens
• last_refill

Advantages

✓ Constant memory usage
✓ Supports burst traffic
✓ No request history stored
✓ Efficient Redis operations
✓ Excellent for distributed systems

Common Use Cases

• API Gateways
• AI APIs
• Public REST APIs
• Reverse Proxies
• SaaS Platforms
• Authentication Services
• Cloud Infrastructure
"""
    )

    print()

    print("=" * 70)

    print("Token Bucket Demo Completed Successfully")

    print("=" * 70)

    print()

    print(
        "Next Example : Leaky Bucket"
    )


# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":

    try:

        #
        # Verify Redis connection before
        # starting the demo.
        #
        redis_client.ping()

        main()

    except redis.ConnectionError:

        print()

        print("=" * 70)

        print("Unable to connect to Redis")

        print("=" * 70)

        print()

        print("Please make sure:")

        print()

        print("1. Redis is installed")

        print("2. Redis Server is running")

        print("3. Host = localhost")

        print("4. Port = 6379")

        print()

    except KeyboardInterrupt:

        print()

        print("=" * 70)

        print("Demo Interrupted")

        print("=" * 70)

        print()

    finally:

        print("Exiting...")

  
