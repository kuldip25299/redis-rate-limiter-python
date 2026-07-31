# How Industry Rate Limiters Work

By now, we've explored three popular rate limiting algorithms.

- Fixed Window Counter
- Sliding Window Log
- Sliding Window Counter

Each algorithm solves the same business problem in a different way.

This naturally raises an important question.

> **Which algorithm do companies actually use in production?**

The answer may surprise you.

There isn't a single "best" algorithm.

Different companies choose different approaches depending on their business requirements, traffic patterns, infrastructure, and performance goals.

Understanding these trade-offs is far more valuable than memorizing algorithms.

---

# There Is No Universal Winner

One of the biggest misconceptions is believing that a newer algorithm automatically replaces an older one.

That isn't how engineering works.

Every algorithm exists because it optimizes for something different.

Some prioritize simplicity.

Some prioritize accuracy.

Others prioritize memory efficiency or burst handling.

Choosing the right algorithm is always a trade-off.

---

# What Do Engineering Teams Consider?

Before selecting a rate limiting strategy, engineers usually ask questions like:

- How many requests does the system receive?
- How accurate must the rate limit be?
- Can occasional bursts be tolerated?
- How much memory can we use?
- Is the application distributed across multiple servers?
- How expensive are rejected requests?

The answers determine which algorithm is the best fit.

---

# Fixed Window Counter

The Fixed Window Counter remains one of the most widely used algorithms because of its simplicity.

It stores only a counter and automatically resets it after a fixed time period.

```
Redis

rate_limit:user:101

↓

Counter
```

### Strengths

- Very simple implementation
- Extremely fast
- Low memory usage
- Easy to scale
- Excellent for many business applications

### Weakness

- Burst traffic at window boundaries

### Common Use Cases

- OTP verification
- Password reset
- Email verification
- Contact forms
- Internal administration tools
- Low to medium traffic APIs

---

# Sliding Window Log

The Sliding Window Log algorithm improves fairness by storing every request timestamp.

Instead of counting requests within a fixed minute, it evaluates the last rolling time window.

```
Redis Sorted Set

10:00:01

10:00:08

10:00:22

10:00:45
```

### Strengths

- Very accurate
- Eliminates burst problems
- Fair request distribution

### Weakness

- Stores every request
- Higher memory usage
- More Redis operations

### Common Use Cases

- Authentication APIs
- Payment APIs
- Premium SaaS platforms
- AI APIs
- Security-sensitive services

---

# Sliding Window Counter

The Sliding Window Counter was created to reduce the memory overhead of Sliding Window Log.

Instead of storing every request, it stores only counters for the current and previous windows.

```
Redis

Previous Counter

Current Counter
```

A weighted calculation estimates the request count.

### Strengths

- Low memory usage
- Smooth request limiting
- Better scalability
- Good balance between accuracy and performance

### Weakness

- Approximate rather than exact
- Slightly more complex calculations

### Common Use Cases

- Large public APIs
- API gateways
- Microservices
- High-volume SaaS platforms

---

# Which Algorithm Is Used by Popular Systems?

Many well-known platforms don't rely on a single algorithm.

Instead, they choose the one that best matches their workload.

| Platform / Product | Common Approach | Why |
|--------------------|-----------------|-----|
| Cloudflare | Token Bucket / Variants | Handles traffic bursts while maintaining throughput |
| NGINX | Leaky Bucket style implementation | Produces a steady request rate |
| Kong API Gateway | Token Bucket and Sliding Window options | Flexible policies for different APIs |
| Envoy Proxy | Token Bucket | Lightweight and efficient for distributed systems |
| AWS API Gateway | Token Bucket style throttling | Supports burst capacity with sustained request limits |
| Stripe APIs | Sliding Window and Token Bucket concepts | Fairness and predictable API usage |

The exact implementation details may vary, but the design goals remain the same: fairness, scalability, and protecting shared resources.

---

# It's Rare to Use Just One Algorithm

Large-scale systems often combine multiple techniques.

For example:

```
Internet

        │

        ▼

Cloudflare

(Token Bucket)

        │

        ▼

API Gateway

(Sliding Window)

        │

        ▼

Application

(Login Limit)

(Fixed Window)
```

Each layer solves a different problem.

The edge protects infrastructure from large traffic spikes.

The API gateway enforces customer-specific limits.

The application applies business rules, such as limiting OTP requests or password reset attempts.

This layered approach provides stronger protection than relying on a single rate limiter.

---

# Choosing the Right Algorithm

There isn't a single correct answer.

Instead, choose the algorithm that best fits the business requirement.

| Requirement | Recommended Algorithm |
|-------------|-----------------------|
| Simple business limits | Fixed Window Counter |
| Maximum accuracy | Sliding Window Log |
| High traffic with low memory usage | Sliding Window Counter |
| Handle burst traffic gracefully | Token Bucket |
| Smooth outgoing request rate | Leaky Bucket |

Always start with the problem, not the algorithm.

---

# A Real Engineering Perspective

One lesson I've learned while building backend systems is that rate limiting is rarely the most complicated part of the architecture.

The difficult part is deciding **what kind of traffic should be limited**.

For example, should every user receive the same limit?

Should premium customers receive higher limits?

Should internal services bypass rate limiting entirely?

Should anonymous users and authenticated users have different quotas?

These business decisions often have a greater impact than the choice of algorithm itself.

A good rate limiter is one that aligns with the product's requirements, not necessarily the most sophisticated implementation.

---

# What's Next?

So far, every algorithm we've studied has focused on **counting requests**.

The next algorithm takes a different approach.

Instead of asking:

> "How many requests has the user already made?"

it asks:

> "Does the user currently have permission to make another request?"

That permission is represented as a **token**.

This simple idea leads us to one of the most widely used production algorithms:

**Token Bucket.**

We'll see how it allows occasional bursts while maintaining a steady long-term request rate, making it a popular choice for API gateways, reverse proxies, and distributed systems.
