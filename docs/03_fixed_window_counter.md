# Fixed Window Counter

The **Fixed Window Counter** is usually the first rate limiting algorithm developers learn, and for good reason. It's simple, fast, and surprisingly effective for many business use cases.

Although more sophisticated algorithms exist, many production systems still use the Fixed Window approach where occasional request bursts are acceptable.

In this chapter, we'll understand the business problem it solves, how it works internally, how Redis makes the implementation simple, and finally build a complete Python implementation.

---

# A Real Business Problem

Let's imagine we're building an OTP verification service.

Whenever a user clicks **"Send OTP"**, our application sends an SMS through a third-party provider.

```
POST /send-otp
```

Under normal circumstances, everything works as expected.

```
+--------+        +-------------+        +---------------+
|  User  | -----> | Application | -----> | SMS Provider  |
+--------+        +-------------+        +---------------+
```

Now imagine a user repeatedly clicks the **Send OTP** button or writes a small script to automate the requests.

```
POST /send-otp

Request 1
Request 2
Request 3
...
Request 500
```

Without any restrictions, our application happily processes every request.

This creates several problems:

- Increased SMS costs
- Unnecessary load on the application
- Possible abuse of the SMS provider
- Poor experience for legitimate users

Clearly, we need a way to limit how frequently a user can request an OTP.

---

# Business Requirement

Suppose the product team defines the following rule:

> A user can request **at most 5 OTPs within one minute**.

If the user exceeds the limit, the application should reject further requests until the minute has passed.

```
Limit

5 Requests

Time Window

60 Seconds
```

Simple enough.

Now the question becomes:

> How do we enforce this efficiently?

---

# The Basic Idea

Instead of storing every request, the Fixed Window algorithm simply keeps a counter.

Whenever a request arrives:

1. Find the user's counter.
2. Increment it.
3. If the counter exceeds the limit, reject the request.
4. Reset the counter automatically after the time window expires.

That's it.

No complicated calculations.

No timestamps.

No background cleanup jobs.

---

# How Redis Helps

Redis is perfect for this problem because it already provides everything we need.

We need:

- A counter
- Automatic expiration
- Fast read/write operations

Redis provides all three.

For every user, we'll create a key like this:

```
rate_limit:user:101
```

The value stored inside Redis is simply the number of requests.

Example:

```
Key

rate_limit:user:101

Value

3
```

If the user makes another request:

```
rate_limit:user:101

Value

4
```

Nothing more.

---

# Redis Commands Used

The Fixed Window algorithm uses only two Redis commands.

## INCR

Increments the counter by one.

```
INCR rate_limit:user:101
```

If the key doesn't exist, Redis automatically creates it.

Example:

```
Doesn't exist

↓

1

↓

2

↓

3

↓

4
```

---

## EXPIRE

Sets how long the key should live.

```
EXPIRE rate_limit:user:101 60
```

After 60 seconds, Redis automatically deletes the key.

This means we never have to manually reset the counter.

---

# Step-by-Step Flow

Suppose the limit is:

```
5 Requests

Per Minute
```

Initially, Redis contains nothing.

```
Redis

(empty)
```

---

## Request 1

```
INCR rate_limit:user:101

Result

1
```

Since this is the first request, we also set an expiration.

```
EXPIRE rate_limit:user:101 60
```

Redis now contains:

```
rate_limit:user:101

Value = 1

TTL = 60 Seconds
```

Request is allowed.

---

## Request 2

```
INCR

Result

2
```

Current Counter

```
2
```

Still below the limit.

Request is allowed.

---

## Request 3

Counter becomes:

```
3
```

Allowed.

---

## Request 4

Counter becomes:

```
4
```

Allowed.

---

## Request 5

Counter becomes:

```
5
```

Allowed.

The user has now reached the configured limit.

---

## Request 6

Redis returns:

```
6
```

Since:

```
6 > 5
```

The application rejects the request.

```
HTTP 429

Too Many Requests
```

---

# What Happens After One Minute?

Remember the expiration we set earlier?

```
EXPIRE

60 Seconds
```

Once the TTL reaches zero:

```
rate_limit:user:101
```

is automatically removed from Redis.

```
Redis

(empty)
```

The next request creates a brand new counter.

The user starts again from zero.

---

# Visual Flow

```
                 Request Arrives
                        │
                        ▼
          INCR rate_limit:user:101
                        │
                        ▼
              Counter Returned
                        │
         ┌──────────────┴──────────────┐
         │                             │
 Counter <= Limit              Counter > Limit
         │                             │
         ▼                             ▼
 Allow Request               Reject Request
```

---

# Why Is It Called a Fixed Window?

The time window never changes while the counter is active.

For example:

```
Window

10:00:00

↓

10:00:59
```

Every request during that period belongs to the same window.

At:

```
10:01:00
```

a completely new window begins with a fresh counter.

This fixed interval is what gives the algorithm its name.

---

# Advantages

The Fixed Window algorithm is popular because it's extremely simple.

Advantages include:

- Very easy to implement
- Excellent performance
- Minimal memory usage
- Uses only a simple Redis counter
- Automatic cleanup using TTL
- Works well for many common business applications

---

# Limitations

The biggest limitation is known as the **Burst Problem**.

Imagine our rule is:

```
5 Requests

Per Minute
```

Now consider the following timeline.

```
10:00:58   Request 1

10:00:58   Request 2

10:00:59   Request 3

10:00:59   Request 4

10:00:59   Request 5
```

The user has reached the limit.

Now the clock moves to:

```
10:01:00
```

A new window starts immediately.

The user can now send:

```
Request 6

Request 7

Request 8

Request 9

Request 10
```

Although the configured limit is **5 requests per minute**, the user has successfully made **10 requests within just a few seconds**.

```
Window 1

★★★★★

↓

Window 2

★★★★★
```

This sudden spike is called a **burst**.

For some systems, this behaviour is perfectly acceptable.

For others, it can become a serious problem.

We'll solve this limitation later using the **Sliding Window** algorithm.

---

# Where Is Fixed Window Commonly Used?

Despite its limitations, the Fixed Window algorithm is still widely used.

Typical use cases include:

- OTP verification
- Password reset requests
- Email verification
- Contact forms
- Public APIs with simple usage limits
- Internal APIs
- Demo applications
- Development environments

Whenever occasional bursts are acceptable, Fixed Window is often the simplest and most cost-effective solution.

---

# Summary

The Fixed Window Counter is the simplest rate limiting algorithm.

Instead of storing every request, it maintains a single counter for each client.

Redis makes the implementation straightforward by providing:

- `INCR` for atomic counters
- `EXPIRE` for automatic window reset

For many business applications, this approach is more than sufficient.

However, it has one important limitation: users can generate bursts of traffic at window boundaries.

In the next chapter, we'll implement this algorithm from scratch in Python using Redis and see exactly how these Redis commands work together in a real application.
