# Sliding Window Counter

In the previous chapter, we implemented the **Sliding Window Log** algorithm.

It solved one of the biggest problems with the Fixed Window approach.

The **burst problem**.

Instead of resetting counters at fixed intervals, it continuously evaluated requests made during the last 60 seconds.

The result was much more accurate rate limiting.

But that accuracy comes with a cost.

For every incoming request, we stored a timestamp inside Redis.

For a small application, that's perfectly acceptable.

For a high-traffic API receiving thousands or even millions of requests every minute, storing every request quickly becomes expensive.

This naturally leads to another question.

> **Can we achieve almost the same accuracy without storing every request?**

That's exactly what the **Sliding Window Counter** algorithm tries to accomplish.

---

# The Problem with Sliding Window Log

Let's revisit our public API example.

Assume one user sends:

```
5,000 Requests

Per Minute
```

With the Sliding Window Log algorithm, Redis stores **5,000 timestamps**.

```
10:00:01

10:00:01

10:00:02

10:00:02

10:00:03

...

10:00:59
```

Now imagine:

```
100 Users
```

Redis stores:

```
500,000 Timestamps
```

Scale that to thousands of users and the memory requirement grows rapidly.

Although the algorithm is accurate, storing every request is not always practical.

---

# A Different Approach

Instead of remembering every request, let's divide time into smaller windows.

For example, instead of storing every request during one minute, we divide the minute into two windows.

```
60 Seconds

-----------------------------

Window A

30 Seconds

+

Window B

30 Seconds
```

Now we only need to store **two counters** instead of hundreds or thousands of timestamps.

---

# The Core Idea

Suppose our current time is:

```
10:00:45
```

The previous 30-second window contains:

```
3 Requests
```

The current window contains:

```
2 Requests
```

Redis stores only:

```
rate_limit:user:101

Current Window

2

Previous Window

3
```

Instead of storing every request, we estimate the request count by combining these two counters.

---

# Why Is This Only an Approximation?

Imagine we're standing at:

```
10:00:45
```

Half of the previous window has already expired.

Not all requests from the previous window should contribute equally.

Requests that happened a long time ago should have less influence.

So instead of adding the counters directly:

```
Current

2

+

Previous

3

=

5
```

we apply a weight.

Suppose only 50% of the previous window still overlaps with the current rolling window.

```
Current

2

+

Previous × 0.5

3 × 0.5

=

3.5
```

This weighted value becomes our estimated request count.

That's why this algorithm is often called a **weighted sliding window**.

---

# Visual Example

```
Previous Window

□□□□□□□□□□

Current Window

■■■■■■■■■■
```

As time moves forward, less of the previous window overlaps with the current one.

```
Previous Window Contribution

100%

↓

80%

↓

60%

↓

40%

↓

20%

↓

0%
```

The contribution decreases smoothly instead of disappearing instantly.

---

# Redis Data Structure

Unlike Sliding Window Log, we don't need a Sorted Set.

We only need counters.

A Redis Hash works well.

Example:

```
rate_limit:user:101

--------------------------

current_window : 2

previous_window : 3
```

Only two numbers.

Regardless of how many requests arrive.

---

# Redis Commands Used

The Sliding Window Counter algorithm typically uses the following Redis commands.

### HSET

Stores the counters.

```
HSET rate_limit:user:101
```

---

### HGETALL

Reads both counters.

```
HGETALL rate_limit:user:101
```

---

### HINCRBY

Increments the current window counter.

```
HINCRBY
```

---

### EXPIRE

Automatically removes inactive users.

```
EXPIRE
```

---

# Request Flow

```
New Request

      │

      ▼

Read Current Counter

Read Previous Counter

      │

      ▼

Calculate Weighted Count

      │

      ▼

Is Count Below Limit?

      │

 ┌────┴────┐

 │         │

Yes        No

 │         │

 ▼         ▼

Increment   Reject

Counter
```

---

# Why Is It Faster?

Sliding Window Log performs operations on every timestamp.

Sliding Window Counter performs operations on only two counters.

That means:

- Less memory
- Fewer Redis operations
- Better performance
- Predictable storage requirements

Regardless of whether a user sends:

```
10 Requests
```

or

```
10,000 Requests
```

the Redis storage remains almost constant.

---

# Is It As Accurate?

Not exactly.

Because the algorithm estimates request counts, it's possible for the calculated value to differ slightly from the actual number of requests.

For most applications, that difference is very small.

In exchange, we significantly reduce memory usage.

This trade-off makes the Sliding Window Counter a popular choice for high-traffic systems.

---

# Advantages

The Sliding Window Counter algorithm offers several benefits.

- Much lower memory usage than Sliding Window Log
- Better scalability
- Smooth request limiting
- Prevents burst traffic
- Constant storage requirements
- Fast Redis operations

---

# Limitations

Like every algorithm, it has trade-offs.

- Uses an estimated request count
- Slightly more complex than Fixed Window
- Less accurate than Sliding Window Log
- Requires weighted calculations

Although it's not perfectly accurate, it's often accurate enough for production systems.

---

# When Should You Use It?

Sliding Window Counter is a great choice when:

- You expect high request volumes
- Memory efficiency is important
- Minor approximation is acceptable
- You need better burst protection than Fixed Window

Typical examples include:

- Public REST APIs
- SaaS platforms
- AI inference APIs
- Search services
- Large internal platforms
- Microservice gateways

---

# Sliding Window Log vs Sliding Window Counter

| Feature | Sliding Window Log | Sliding Window Counter |
|----------|--------------------|------------------------|
| Accuracy | Excellent | Very Good |
| Memory Usage | High | Low |
| Redis Data Structure | Sorted Set | Hash / Counter |
| Stores Every Request | Yes | No |
| Performance | Good | Better |
| Burst Protection | Excellent | Excellent |
| Implementation | Moderate | Moderate |

---

# Summary

The Sliding Window Counter algorithm is an optimization of the Sliding Window Log approach.

Instead of storing every request timestamp, it stores only a few counters and estimates how many requests occurred during the current rolling window.

Although the result is approximate rather than exact, the reduction in memory usage makes it a practical choice for many production systems handling large volumes of traffic.

In the next chapter, we'll implement the Sliding Window Counter algorithm in Python using Redis and see how weighted counting works in practice.
