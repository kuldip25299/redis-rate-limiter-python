"""
Leaky Bucket Rate Limiter using Redis

Business Rule
-------------
Accept requests until the queue reaches its
maximum capacity.

Requests are processed at a constant rate.

Redis Data Structure
--------------------
List

Redis Commands Used
-------------------
RPUSH
LPOP
LLEN
LRANGE
EXPIRE

Python Version
--------------
Python 3.12+

Run
---
python examples/05_leaky_bucket.py
"""

import time
from datetime import datetime

import redis

# ==========================================================
# Configuration
# ==========================================================

REDIS_HOST = "localhost"
REDIS_PORT = 6379

# Maximum requests allowed in queue
QUEUE_CAPACITY = 5

# Seconds between processing requests
LEAK_INTERVAL = 2

# Redis key expiry
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
    Build Redis queue key.
    """
    return f"leaky_bucket:{user_id}"


def print_line():
    print("-" * 70)


def print_header(title: str):

    print()

    print("=" * 70)

    print(title)

    print("=" * 70)


# ==========================================================
# Queue Visualization
# ==========================================================


def queue_visual(user_id: str):

    queue = redis_client.lrange(
        redis_key(user_id),
        0,
        -1,
    )

    print()

    print("Current Queue")

    print_line()

    if not queue:

        print("(empty)")

        return

    for request in queue:

        print(f"[ {request} ]")

    print()

    print(f"Queue Size : {len(queue)} / {QUEUE_CAPACITY}")


# ==========================================================
# Redis Inspection
# ==========================================================


def print_queue_state(user_id: str):

    key = redis_key(user_id)

    queue = redis_client.lrange(
        key,
        0,
        -1,
    )

    print()

    print("Redis List")

    print_line()

    print(f"Redis Key : {key}")

    print()

    if not queue:

        print("(empty)")

        return

    for item in queue:

        print(item)


# ==========================================================
# Accept Request
# ==========================================================


def add_request(
    user_id: str,
    request_id: str,
) -> bool:
    """
    Add request to queue.

    Returns True if accepted.

    Returns False if queue is full.
    """

    key = redis_key(user_id)

    queue_size = redis_client.llen(key)

    print()

    print("Current Time")

    print("--------------------------------")

    print(
        datetime.now().strftime("%H:%M:%S")
    )

    print()

    print(f"Queue Size : {queue_size}")

    print(f"Capacity   : {QUEUE_CAPACITY}")

    if queue_size >= QUEUE_CAPACITY:

        print()

        print("Decision")

        print("❌ Queue Full")

        print()

        queue_visual(user_id)

        return False

    redis_client.rpush(
        key,
        request_id,
    )

    redis_client.expire(
        key,
        KEY_EXPIRY,
    )

    print()

    print("Decision")

    print("✅ Request Accepted")

    queue_visual(user_id)

    return True


# ==========================================================
# Process Request
# ==========================================================


def process_request(user_id: str):
    """
    Remove oldest request from queue.
    """

    key = redis_key(user_id)

    request = redis_client.lpop(key)

    if request is None:

        print()

        print("Processor")

        print("--------------------------------")

        print("Queue Empty")

        return

    print()

    print("Processor")

    print("--------------------------------")

    print(f"Processing : {request}")

    queue_visual(user_id)

# ==========================================================
# Cleanup
# ==========================================================


def reset_queue(user_id: str):
    """
    Delete the Redis queue.

    This ensures every demo starts
    with a clean state.
    """

    redis_client.delete(redis_key(user_id))


# ==========================================================
# Business Explanation
# ==========================================================


def print_business_rule():

    print_header("Leaky Bucket Rate Limiter")

    print("Business Rule")

    print_line()

    print(f"Queue Capacity : {QUEUE_CAPACITY}")

    print(f"Leak Interval  : {LEAK_INTERVAL} Seconds")

    print()

    print(
        "Incoming requests are immediately added "
        "to the queue.\n"
        "Requests leave the queue at a constant rate."
    )


def explain_bucket():

    print_header("How Leaky Bucket Works")

    print(
        """
Imagine a bucket with a small hole.

Water can be poured into the bucket
at any speed.

Sometimes slowly.

Sometimes very quickly.

However...

Water always leaks from the bottom
at the same speed.

The Leaky Bucket algorithm works
exactly the same way.

Incoming requests

↓

Queue

↓

Constant Processing Rate

The queue absorbs bursts while
keeping downstream systems stable.
"""
    )


# ==========================================================
# Redis Explanation
# ==========================================================


def explain_redis_storage():

    print_header("Redis Storage")

    print(
        """
Redis stores the queue as a List.

Example

leaky_bucket:101

-----------------------------------

REQ-1

REQ-2

REQ-3

REQ-4

-----------------------------------

RPUSH

Adds a request to the end.

LPOP

Removes the oldest request.

LLEN

Returns queue size.

Unlike Token Bucket,

every waiting request exists inside
Redis until it is processed.
"""
    )


# ==========================================================
# Demo Helpers
# ==========================================================


def wait_with_progress(seconds: int):

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


def submit_requests(user_id: str):

    print_header("Submitting Requests")

    #
    # Try adding more requests than
    # the queue can hold.
    #
    for request_number in range(1, 8):

        print()

        print_line()

        request_id = f"REQ-{request_number}"

        print(f"Incoming {request_id}")

        add_request(
            user_id=user_id,
            request_id=request_id,
        )

        #
        # Small delay so readers
        # can follow the output.
        #
        time.sleep(1)


def process_queue(user_id: str):

    print_header("Processing Queue")

    #
    # Keep processing until the queue
    # becomes empty.
    #
    while True:

        queue_size = redis_client.llen(
            redis_key(user_id)
        )

        if queue_size == 0:

            break

        process_request(user_id)

        #
        # Simulate constant processing.
        #
        wait_with_progress(
            LEAK_INTERVAL
        )

    print()

    print("All queued requests have been processed.")


# ==========================================================
# Algorithm Explanation
# ==========================================================


def explain_algorithm():

    print_header("Request Processing Flow")

    print(
        """
                    New Request
                         │
                         ▼
                 Is Queue Full?
                  ┌──────┴──────┐
                  │             │
                No              Yes
                  │             │
                  ▼             ▼
          Add Request       Reject Request
              To Queue
                  │
                  ▼
          Wait For Processing
                  │
                  ▼
      Remove Oldest Request (LPOP)
                  │
                  ▼
           Process The Request

Notice something important.

Requests are accepted immediately,
but they are NOT processed immediately.

The queue controls the processing rate,
keeping downstream systems stable.
"""
    )


# ==========================================================
# Final Summary
# ==========================================================


def print_summary():

    print_header("Summary")

    print(
        f"""
Queue Capacity : {QUEUE_CAPACITY}

Leak Interval  : {LEAK_INTERVAL} Seconds

Redis Commands Used

• RPUSH
• LPOP
• LLEN
• LRANGE
• EXPIRE

Advantages

✓ Smooth request processing
✓ Predictable server load
✓ Simple implementation
✓ Protects downstream systems
✓ Easy to visualize

Trade-offs

• Requests may wait in queue
• Increased response time
• Queue size must be managed
• Burst traffic is delayed

Typical Use Cases

• Payment Processing
• Email Sending
• Notification Systems
• Video Processing
• Image Conversion
• Background Jobs
• Message Queues
"""
    )


# ==========================================================
# Main
# ==========================================================


def main():

    user_id = "101"

    #
    # Always begin with an empty queue.
    #
    reset_queue(user_id)

    print_business_rule()

    explain_bucket()

    explain_redis_storage()

    explain_algorithm()

    #
    # Demonstration
    #
    submit_requests(user_id)

    print()

    print("=" * 70)

    print("Incoming traffic has stopped.")

    print("The processor continues working...")

    print("=" * 70)

    process_queue(user_id)

    #
    # Final Redis state
    #
    print_header("Final Redis State")

    print_queue_state(user_id)

    #
    # Summary
    #
    print_summary()

    print()

    print("=" * 70)

    print("Leaky Bucket Demo Completed Successfully")

    print("=" * 70)

    print()

    print("Next Chapter : Algorithm Comparison")


# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":

    try:

        #
        # Verify Redis connection.
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

        print("1. Redis Server is running")

        print("2. Host = localhost")

        print("3. Port = 6379")

        print()

    except KeyboardInterrupt:

        print()

        print("=" * 70)

        print("Demo Interrupted")

        print("=" * 70)

        print()

    finally:

        print("Exiting...")
