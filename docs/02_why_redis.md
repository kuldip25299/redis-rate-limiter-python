# Why Redis Became the Standard Choice for Rate Limiting

After understanding why applications need rate limiting, the next question is usually:

> **Why is Redis used in almost every Rate Limiting implementation?**

Technically, Redis isn't the only option.

You could build a rate limiter using MySQL, PostgreSQL, MongoDB, or even an in-memory Python dictionary.

The real question is:

> **Which solution continues to perform well as traffic grows?**

This chapter explains why Redis has become the preferred choice for implementing distributed rate limiters.

---

# The Simplest Approach

Imagine we're building an OTP service.

We decide to store every OTP request in a database table.

```
otp_requests

+----+---------+---------------------+
| ID | USER_ID | CREATED_AT          |
+----+---------+---------------------+
| 1  | 101     | 10:00:05            |
| 2  | 101     | 10:00:17            |
| 3  | 101     | 10:00:29            |
+----+---------+---------------------+
```

Whenever a new request arrives, we execute:

```
SELECT COUNT(*)
FROM otp_requests
WHERE user_id = 101
AND created_at > NOW() - INTERVAL 1 MINUTE;
```

If the count is less than our limit, we allow the request.

Otherwise, we reject it.

Simple.

It works.

So why isn't everyone doing this?

---

# The Problem with Traditional Databases

Imagine your application receives:

- 10 users
- 100 users
- 1,000 users
- 10,000 users
- 100,000 users

Every incoming request now performs:

- A database read
- Sometimes a database write
- Transaction handling
- Disk operations
- Index lookups
- Lock management

Your primary database now spends a significant amount of time answering one simple question:

> **How many requests has this user made?**

That's not an efficient use of your database.

Your database should be busy storing business data—not acting as a request counter.

---

# Rate Limiting Is a Counter Problem

At its core, most rate limiters repeatedly ask one question:

```
Has this client exceeded the allowed limit?
```

To answer that question, we usually need to:

- Read a value
- Increment a value
- Reset it after some time

That's essentially a counter.

For counters, an in-memory data store is a much better fit than a relational database.

---

# Why Redis Fits So Well

Redis was designed for fast, in-memory operations.

Unlike traditional databases, Redis keeps its data in memory, allowing operations to complete in microseconds instead of milliseconds.

For a rate limiter, that's exactly what we need.

Every request typically performs just two operations:

```
Increment Counter

↓

Check Current Value
```

Redis can do both extremely quickly.

---

# Atomic Operations

Consider two requests arriving at exactly the same moment.

```
User 101

Request A

Request B
```

If both requests try to increase the counter simultaneously, we must ensure they don't overwrite each other.

Redis provides atomic commands.

For example:

```
INCR user:101
```

Even if thousands of requests arrive concurrently, Redis guarantees that every increment happens safely.

No race conditions.

No duplicate counts.

No additional locking logic in your application.

---

# Automatic Expiration (TTL)

One of Redis's most useful features for rate limiting is key expiration.

Imagine our rule is:

```
5 requests

per minute
```

After one minute, we no longer care about the old counter.

Instead of deleting it ourselves, Redis can remove it automatically.

```
user:101

Value = 5

TTL = 60 seconds
```

Once the timer reaches zero, Redis deletes the key automatically.

No scheduled jobs.

No cleanup scripts.

No manual maintenance.

---

# Common Redis Commands Used

Most rate limiting algorithms rely on only a handful of Redis commands.

## INCR

Increases a numeric value by one.

```
INCR user:101
```

Example:

```
1

↓

2

↓

3

↓

4
```

This is the foundation of simple counter-based algorithms.

---

## EXPIRE

Sets how long a key should exist.

```
EXPIRE user:101 60
```

After 60 seconds, Redis removes the key automatically.

---

## GET

Returns the current value.

```
GET user:101
```

Useful when checking the current request count.

---

## SET

Stores a value.

```
SET user:101 1
```

Some algorithms store counters directly using `SET`.

---

## DEL

Removes a key.

```
DEL user:101
```

Useful when resetting counters manually.

---

## ZADD

Adds a timestamp to a Sorted Set.

```
ZADD requests:101
```

Used by Sliding Window Log.

We'll explore this algorithm later.

---

## ZCOUNT

Counts how many timestamps fall within a time range.

Also used by Sliding Window Log.

---

## ZREMRANGEBYSCORE

Removes expired timestamps.

This prevents Sorted Sets from growing indefinitely.

---

# Redis Data Structures Used

Different algorithms use different Redis data structures.

| Algorithm | Redis Data Structure |
|------------|----------------------|
| Fixed Window | String |
| Sliding Window Log | Sorted Set |
| Sliding Window Counter | String |
| Token Bucket | Hash |
| Leaky Bucket | List / Sorted Set |

We'll examine each implementation in detail throughout this repository.

---

# Why Not an In-Memory Python Dictionary?

A common question is:

> Why not simply store counters in a Python dictionary?

For a single application instance, that works.

However, production systems rarely run only one server.

Imagine three application servers behind a load balancer.

```
                Load Balancer
                     │
        ┌────────────┼────────────┐
        │            │            │
     App 1        App 2        App 3
```

If each server maintains its own dictionary:

```
App 1

User 101 = 3

App 2

User 101 = 1

App 3

User 101 = 2
```

No server has the complete picture.

A user could exceed the intended limit simply by having requests distributed across different servers.

Redis solves this by acting as a shared, central store.

Every application server reads from and writes to the same counters.

---

# Why Redis Became the Industry Standard

Redis offers several characteristics that make it particularly well suited for rate limiting.

- Extremely fast in-memory operations
- Atomic updates
- Automatic key expiration
- Simple data structures
- Excellent support for counters
- Easy to scale across multiple application servers

These capabilities allow developers to build reliable distributed rate limiters with relatively little code.

---

# What's Next?

Now that we understand why Redis is commonly used, it's time to build our first rate limiter.

In the next chapter, we'll implement the simplest algorithm:

**Fixed Window Counter**

We'll start with the business problem, understand how the algorithm works, and then build a complete Python implementation that you can run locally using Redis.
