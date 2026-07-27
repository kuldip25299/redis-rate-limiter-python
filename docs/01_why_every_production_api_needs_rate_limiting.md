# Why Every Production API Needs Rate Limiting

If you've built backend systems long enough, you've probably implemented some form of rate limiting—even if you didn't initially call it that.

Maybe it was limiting OTP requests to prevent SMS abuse. Maybe it was restricting failed login attempts to reduce brute-force attacks. Or perhaps it was protecting a public API from a single client consuming all available resources.

Regardless of the use case, the underlying problem is the same:

> **How do we prevent a single user, client, or application from sending more requests than our system is designed to handle?**

That's exactly the problem rate limiting is designed to solve.

This chapter isn't about Redis or implementation details. Before writing a single line of code, it's worth understanding the business problems that led to rate limiting becoming a standard part of modern backend systems.

---

# A Simple Business Problem

Imagine you're building an OTP verification service.

A user enters their mobile number and requests an OTP.

```
POST /send-otp
```

Under normal circumstances, the flow is straightforward.

```
User
   │
   │ Request OTP
   ▼
Application
   │
   ▼
SMS Provider
   │
   ▼
OTP Delivered
```

Now imagine someone writes a simple script that sends the same request thousands of times.

```
POST /send-otp

100 requests...

1,000 requests...

10,000 requests...
```

Every request triggers another SMS.

Within minutes:

- Your SMS costs increase dramatically.
- Legitimate users experience delays.
- The SMS provider may temporarily block your account.
- Your infrastructure spends resources processing requests that should never have been accepted.

The problem isn't your OTP logic.

The problem is that nothing prevents excessive requests.

---

# It's Not Just About Security

When people hear "rate limiting", they often think about stopping hackers.

In reality, most production systems use rate limiting to protect resources rather than defend against attacks.

Some common examples include:

| System | Why Rate Limiting Matters |
|---------|---------------------------|
| OTP Service | Prevent SMS abuse and unnecessary costs |
| Login API | Reduce brute-force password attempts |
| Password Reset | Prevent email flooding |
| Public REST API | Ensure fair usage across clients |
| AI API | Control expensive model inference requests |
| Payment API | Prevent accidental duplicate payments |
| File Upload Service | Protect storage and bandwidth |
| Search API | Avoid excessive database queries |

In many cases, users aren't acting maliciously.

A buggy client, a retry loop, or an application error can generate thousands of requests unintentionally.

Rate limiting protects your system regardless of the cause.

---

# What Happens Without Rate Limiting?

Without request limits, a single client can consume a disproportionate amount of system resources.

Imagine your API can comfortably process 1,000 requests per second.

Now consider one client sending 900 requests every second.

```
Capacity

1000 Requests / Second

───────────────

Client A

900 Requests

Client B

40 Requests

Client C

30 Requests

Client D

20 Requests

Client E

10 Requests
```

Technically, the server is still within its capacity.

Practically, almost all available resources are being consumed by one client.

The result is poor response times for everyone else.

Rate limiting ensures that available capacity is shared fairly across users.

---

# So, What Is Rate Limiting?

Rate limiting is the process of restricting how many requests a client can make within a specified period of time.

For example:

```
Maximum Requests

5 requests

Time Window

1 minute
```

If a user sends:

```
Request 1   ✅ Allowed

Request 2   ✅ Allowed

Request 3   ✅ Allowed

Request 4   ✅ Allowed

Request 5   ✅ Allowed

Request 6   ❌ Rejected
```

The application temporarily blocks additional requests until the limit resets.

The exact way this limit is enforced depends on the algorithm being used, which we'll explore in later chapters.

---

# What Can We Rate Limit?

The "client" doesn't always mean a user.

In practice, systems apply rate limits using many different identifiers.

For example:

- User ID
- IP Address
- API Key
- Session ID
- Mobile Number
- Email Address
- Access Token
- Device ID
- Individual API Endpoint

Different applications choose different identifiers depending on the business requirement.

---

# What Makes a Good Rate Limiter?

A production-ready rate limiter should satisfy a few important goals.

It should:

- Process requests quickly.
- Scale across multiple application servers.
- Produce consistent results.
- Prevent abuse without blocking legitimate users.
- Introduce minimal overhead to request processing.

As traffic grows, maintaining these properties becomes increasingly difficult, which is why the choice of algorithm matters.

No single algorithm is perfect for every workload.

Each one makes different trade-offs between accuracy, memory usage, burst handling, and implementation complexity.

We'll compare those trade-offs throughout this repository.

---

# Where Does Redis Fit In?

At this point, we've only discussed the business problem.

The next question naturally becomes:

> Where should we store request counts?

A traditional relational database can certainly keep track of requests, but it's rarely the best tool for this job.

Modern rate limiters typically rely on Redis because it provides:

- Extremely fast in-memory operations
- Atomic counters
- Automatic key expiration (TTL)
- Efficient data structures
- Consistent performance under high traffic

In the next chapter, we'll explore why Redis has become the standard choice for implementing distributed rate limiters.

---

# What's Next?

Now that we've established why production systems need rate limiting, the next step is understanding why Redis is such a natural fit for solving this problem.

In the next chapter we'll cover:

- Why not MySQL or PostgreSQL?
- Why Redis performs so well for counters
- The Redis commands commonly used by rate limiters
- The Redis data structures behind different algorithms

Once those fundamentals are clear, we'll start implementing each rate limiting algorithm from scratch using Python.
