# Rate Limiting Algorithm Comparison

By this point, we've explored five different rate limiting algorithms.

Each one solves the same problem—protecting an application from excessive requests—but they do it in different ways.

A common question developers ask is:

> **"Which algorithm should I use?"**

The answer is simple:

> **There is no single best algorithm.**

Every algorithm has strengths and trade-offs.

The right choice depends on your business requirements, traffic patterns, and user experience.

This chapter compares all the algorithms we've implemented so you can quickly understand when each one makes sense.

---

# Quick Comparison

| Feature | Fixed Window Counter | Sliding Window Log | Sliding Window Counter | Token Bucket | Leaky Bucket |
|----------|----------------------|--------------------|------------------------|--------------|--------------|
| Easy to Understand | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐☆ | ⭐⭐⭐☆☆ | ⭐⭐⭐⭐☆ | ⭐⭐⭐⭐☆ |
| Easy to Implement | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐☆ | ⭐⭐⭐☆☆ | ⭐⭐⭐⭐☆ | ⭐⭐⭐⭐☆ |
| Memory Usage | Very Low | High | Low | Very Low | Low |
| Request Accuracy | Good | Excellent | Very Good | Excellent | Excellent |
| Allows Burst Traffic | Poor | Good | Good | Excellent | No |
| Constant Processing Rate | No | No | No | No | Yes |
| Redis Memory Growth | Constant | Grows With Requests | Constant | Constant | Grows With Queue |
| Production Usage | Common | Common | Very Common | Very Common | Common |

---

# Redis Data Structures

Each algorithm stores data differently.

| Algorithm | Redis Data Structure | Why |
|-----------|----------------------|-----|
| Fixed Window Counter | String | Stores a simple request count |
| Sliding Window Log | Sorted Set | Stores every request timestamp |
| Sliding Window Counter | Hash | Stores counters for adjacent windows |
| Token Bucket | Hash | Stores remaining tokens and last refill time |
| Leaky Bucket | List | Stores queued requests |

Choosing the right Redis data structure is just as important as choosing the algorithm itself.

---

# Memory Usage Comparison

Memory usage becomes important when your application serves thousands or millions of users.

| Algorithm | Memory Usage |
|-----------|--------------|
| Fixed Window Counter | ⭐ Excellent |
| Sliding Window Log | ⭐⭐⭐⭐⭐ Highest |
| Sliding Window Counter | ⭐⭐ Low |
| Token Bucket | ⭐ Excellent |
| Leaky Bucket | ⭐⭐ Low |

### Why?

**Fixed Window Counter**

Stores only a single number.

```
user:101

count = 4
```

---

**Sliding Window Log**

Stores every request timestamp.

```
10:00:01

10:00:04

10:00:07

10:00:12
```

More requests mean more Redis memory.

---

**Sliding Window Counter**

Stores only aggregated counters.

```
Current Window

Previous Window
```

Memory stays small.

---

**Token Bucket**

Stores only two values.

```
tokens

last_refill
```

Memory remains constant.

---

**Leaky Bucket**

Stores queued requests.

Memory depends on queue size rather than request history.

---

# Burst Traffic

One of the biggest differences between these algorithms is how they handle bursts.

## Fixed Window Counter

```
Minute Ends

↓

Counter Resets

↓

Large Burst Possible
```

This is the classic "window boundary" problem.

---

## Sliding Window Log

```
Rolling Window

↓

Smooth Decision

↓

Minimal Burst
```

Very fair.

---

## Sliding Window Counter

Uses weighted counters to reduce burst effects while using less memory.

---

## Token Bucket

```
★★★★★

Stored Tokens

↓

Burst Allowed
```

Excellent when users occasionally perform many actions in a short time.

---

## Leaky Bucket

```
Incoming Requests

↓

Queue

↓

Constant Output
```

No bursts.

Every request waits its turn.

---

# Accuracy

| Algorithm | Accuracy |
|-----------|----------|
| Fixed Window Counter | Good |
| Sliding Window Log | Excellent |
| Sliding Window Counter | Very Good |
| Token Bucket | Excellent |
| Leaky Bucket | Excellent |

Sliding Window Log provides the most accurate rolling window calculation because every request is tracked individually.

Sliding Window Counter trades a small amount of accuracy for much better memory efficiency.

---

# Performance

| Algorithm | Performance |
|-----------|-------------|
| Fixed Window Counter | Excellent |
| Sliding Window Log | Good |
| Sliding Window Counter | Excellent |
| Token Bucket | Excellent |
| Leaky Bucket | Very Good |

The more Redis operations and data you store, the more work Redis has to perform.

Algorithms with constant storage generally scale better under heavy load.

---

# Scalability

All five algorithms work well with Redis, but some scale more naturally than others.

| Algorithm | Scalability |
|-----------|-------------|
| Fixed Window Counter | Excellent |
| Sliding Window Log | Good |
| Sliding Window Counter | Excellent |
| Token Bucket | Excellent |
| Leaky Bucket | Very Good |

Sliding Window Log may require additional memory tuning as traffic increases because every request is stored until it expires.

---

# Which Algorithm Is the Simplest?

If your business requirement is straightforward, you don't need a complicated algorithm.

| Business Rule | Suggested Algorithm |
|--------------|---------------------|
| 5 OTP requests per hour | Fixed Window Counter |
| 5 password resets per day | Fixed Window Counter |
| Contact form submissions | Fixed Window Counter |

Simple business rules are often best solved with simple algorithms.

---

# Which Algorithm Is the Most Accurate?

If fairness is your highest priority:

```
Sliding Window Log
```

It evaluates requests within a true rolling time window and avoids the boundary issues of Fixed Window Counter.

The trade-off is increased memory usage.

---

# Which Algorithm Handles Bursts Best?

If users naturally work in short bursts:

```
Token Bucket
```

Examples include:

- Mobile applications
- AI APIs
- Public REST APIs
- Dashboard loading
- File uploads

Users can briefly exceed the average request rate without overwhelming the system.

---

# Which Algorithm Protects Downstream Services?

If the goal is to smooth traffic before it reaches another service:

```
Leaky Bucket
```

Examples include:

- Payment processing
- Email sending
- Notification delivery
- Background jobs
- Image processing

Requests are processed at a steady rate instead of all at once.

---

# Which Algorithm Would I Choose?

If I were building a new backend application today, my thought process would be something like this:

| Situation | My Choice |
|----------|-----------|
| Simple business limits | Fixed Window Counter |
| Maximum fairness | Sliding Window Log |
| High traffic APIs | Sliding Window Counter |
| Public APIs | Token Bucket |
| Traffic shaping | Leaky Bucket |

I wouldn't start by asking:

> **"Which algorithm is the most advanced?"**

I'd start by asking:

> **"What problem am I trying to solve?"**

The algorithm should always support the business requirement—not the other way around.

---

# Final Thoughts

Every algorithm in this repository has a place in production systems.

Some prioritize simplicity.

Some prioritize fairness.

Some prioritize memory efficiency.

Others prioritize a smooth and predictable request flow.

Understanding these trade-offs is far more valuable than memorizing implementation details.

Once you understand **why** an algorithm exists, choosing the right one becomes much easier.

The best rate limiter isn't the one with the most sophisticated implementation.

It's the one that solves your business problem with the least complexity.
