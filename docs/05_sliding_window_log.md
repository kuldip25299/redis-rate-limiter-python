# Sliding Window Log

In the previous chapter, we saw the biggest limitation of the Fixed Window algorithm.

Although the configured limit was **5 requests per minute**, a user was able to send **10 requests within a few seconds** simply because the counter reset at the start of a new window.

The algorithm wasn't incorrect.

It did exactly what it was designed to do.

The problem is that a **fixed time window doesn't always reflect how users actually send requests**.

Instead of grouping requests into rigid one-minute intervals, what if we always looked at the **last 60 seconds**, regardless of when the request arrived?

That's exactly what the Sliding Window Log algorithm does.

---

# Revisiting Our Business Requirement

Let's continue using the same OTP service.

The business rule hasn't changed.

> A user can request **at most 5 OTPs during any 60-second period.**

Notice the wording.

It no longer says:

```
5 Requests

Per Calendar Minute
```

Instead it means:

```
Any Rolling 60 Seconds
```

That small difference completely changes how we implement the rate limiter.

---

# Why a Counter Is No Longer Enough

The Fixed Window algorithm only stores one number.

```
rate_limit:user:101

Value = 4
```

That worked because every request belonged to the same window.

But now our window keeps moving every second.

To know how many requests occurred during the **last 60 seconds**, we need to know **when every request happened**.

Instead of storing only a counter, we'll store timestamps.

---

# The Core Idea

Every request is recorded with the exact time it occurred.

Example:

```
User 101

10:00:05

10:00:12

10:00:27

10:00:41

10:00:55
```

Whenever a new request arrives, we simply ask:

> "Which of these requests happened during the last 60 seconds?"

Older requests are ignored.

---

# Why Redis Sorted Sets?

Redis provides a data structure called a **Sorted Set**, which is perfect for this problem.

A Sorted Set stores values together with a numeric score.

For rate limiting:

```
Score

↓

Request Timestamp
```

Example:

```
Key

rate_limit:user:101

--------------------------------

Score          Member

1714557605     request-1

1714557612     request-2

1714557627     request-3

1714557641     request-4

1714557655     request-5
```

Redis automatically keeps the entries sorted by timestamp.

That makes time-based operations extremely efficient.

---

# Redis Commands Used

Unlike Fixed Window, Sliding Window Log uses a few additional Redis commands.

---

## ZADD

Adds a request timestamp.

```
ZADD rate_limit:user:101
```

Every incoming request creates a new entry.

---

## ZREMRANGEBYSCORE

Removes expired requests.

```
Remove everything older than

Current Time - 60 Seconds
```

This keeps the Sorted Set small.

---

## ZCARD

Counts how many requests remain.

If the count exceeds our configured limit, we reject the request.

---

## EXPIRE

Adds a TTL to the Redis key.

If the user becomes inactive, Redis automatically removes the Sorted Set.

---

# Step-by-Step Example

Our limit is still:

```
5 Requests

60 Seconds
```

Initially Redis contains nothing.

```
Redis

(empty)
```

---

## Request 1

Time

```
10:00:05
```

Redis stores:

```
10:00:05
```

Request Count

```
1
```

Allowed.

---

## Request 2

```
10:00:18
```

Redis now stores:

```
10:00:05

10:00:18
```

Count

```
2
```

Allowed.

---

## Request 3

```
10:00:31
```

Redis

```
10:00:05

10:00:18

10:00:31
```

Count

```
3
```

Allowed.

---

## Request 4

```
10:00:45
```

Redis

```
10:00:05

10:00:18

10:00:31

10:00:45
```

Allowed.

---

## Request 5

```
10:00:58
```

Redis

```
10:00:05

10:00:18

10:00:31

10:00:45

10:00:58
```

Count

```
5
```

Allowed.

---

## Request 6

A new request arrives at:

```
10:01:02
```

Before counting, Redis removes everything older than:

```
10:00:02
```

Nothing is removed because every request is still within the last 60 seconds.

Current request count:

```
6
```

The request is rejected.

---

# What Happens Later?

Now imagine another request arrives at:

```
10:01:10
```

Before processing it, Redis removes requests older than:

```
10:00:10
```

The first request occurred at:

```
10:00:05
```

That request is now outside the rolling window.

Redis automatically removes it.

Remaining requests:

```
10:00:18

10:00:31

10:00:45

10:00:58
```

Current count:

```
4
```

The new request is accepted.

Notice something important.

The window didn't reset.

It simply moved forward.

That's why it's called a **Sliding Window**.

---

# Visual Timeline

```
Time
────────────────────────────────────────────>

10:00:05 ●

10:00:18 ●

10:00:31 ●

10:00:45 ●

10:00:58 ●

               ▲

         Current Time

Only requests within the last

60 seconds

are counted.
```

Unlike Fixed Window, there is never a sudden reset.

---

# Request Processing Flow

```
               New Request
                     │
                     ▼
      Remove Expired Timestamps
                     │
                     ▼
          Count Remaining Requests
                     │
          ┌──────────┴──────────┐
          │                     │
      Count < Limit        Count >= Limit
          │                     │
          ▼                     ▼
 Add New Timestamp        Reject Request
          │
          ▼
     Allow Request
```

---

# Why Is It More Accurate?

The Sliding Window Log algorithm always considers the **last 60 seconds**.

There are no fixed calendar boundaries.

Because of that, users cannot exploit the transition between two windows to send large bursts of traffic.

The request history continuously moves forward with time.

This makes the algorithm much fairer than Fixed Window.

---

# Advantages

The Sliding Window Log algorithm offers several benefits.

- Prevents burst traffic at window boundaries
- Very accurate request counting
- Fair request distribution
- Easy to understand
- Suitable for distributed systems
- Works well with Redis Sorted Sets

---

# Limitations

The increased accuracy comes with a cost.

Unlike Fixed Window, every request must be stored individually.

That means:

- Higher memory usage
- More Redis operations
- Slightly slower than a simple counter
- Memory grows with request volume

For users generating thousands of requests per minute, the Sorted Set can become quite large.

This is the biggest trade-off of the algorithm.

---

# When Should You Use Sliding Window Log?

This algorithm is a good choice when accuracy is more important than memory usage.

Typical examples include:

- Public REST APIs
- AI APIs
- Payment APIs
- SaaS platforms
- Authentication services
- Stock market APIs
- High-value business operations

Whenever burst traffic is unacceptable, Sliding Window Log is usually a better choice than Fixed Window.

---

# Summary

The Sliding Window Log algorithm improves upon Fixed Window by replacing a simple counter with a timestamp log.

Instead of asking:

> "How many requests were made during this calendar minute?"

it asks:

> "How many requests have been made during the last 60 seconds?"

This small change eliminates the burst problem and provides much more accurate rate limiting.

The trade-off is increased memory usage because every request timestamp must be stored.

In the next chapter, we'll implement the Sliding Window Log algorithm in Python using Redis Sorted Sets and see these Redis commands working together in a real application.
