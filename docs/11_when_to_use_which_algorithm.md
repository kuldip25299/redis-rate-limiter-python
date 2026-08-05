# When to Use Which Rate Limiting Algorithm

By now, we've explored five different rate limiting algorithms and built a working Python implementation for each one.

A question I often hear from developers is:

> **"Which algorithm should I use?"**

The answer is always the same.

> **Start with the business problem, not the algorithm.**

Every algorithm exists because it solves a different problem.

Some prioritize simplicity.

Some prioritize fairness.

Some allow burst traffic.

Others intentionally slow traffic down to protect downstream systems.

This chapter maps common backend scenarios to the algorithm that best fits the requirement.

---

# 1. OTP Verification

## Business Requirement

A user should be able to request an OTP only **5 times per hour**.

```
Send OTP

↓

Maximum 5 Requests

↓

Block Additional Requests
```

## Recommended Algorithm

**Fixed Window Counter**

## Why?

The business rule is simple.

The limit resets every hour.

A small burst near the window boundary usually isn't a problem.

### Why Not Other Algorithms?

- Sliding Window is unnecessary for such a simple rule.
- Token Bucket adds unnecessary complexity.
- Leaky Bucket doesn't solve this problem.

---

# 2. Password Reset

## Business Requirement

Allow only **3 password reset requests per day**.

```
Forgot Password

↓

3 Requests Per Day

↓

Reject Additional Requests
```

## Recommended Algorithm

**Fixed Window Counter**

## Why?

This is another simple business rule.

A counter with an expiration time is all that's needed.

---

# 3. Login Attempts

## Business Requirement

Protect the application from brute-force login attempts.

```
Login

↓

5 Failed Attempts

↓

Temporarily Block User
```

## Recommended Algorithm

**Sliding Window Log**

## Why?

A rolling time window provides much better protection than a fixed window.

It avoids situations where an attacker waits for the counter to reset before trying again.

Accuracy is more important than memory usage for authentication.

---

# 4. Public REST APIs

## Business Requirement

Allow users to call an API without overwhelming the backend.

```
GET /products

POST /orders

GET /users
```

## Recommended Algorithm

**Token Bucket**

## Why?

Users often make several requests in a short period.

For example:

- Opening a dashboard
- Loading multiple resources
- Refreshing data

Allowing these short bursts improves the user experience while still controlling the long-term request rate.

---

# 5. AI APIs

## Business Requirement

Protect expensive AI models from excessive usage.

Examples:

```
POST /chat

POST /generate-text

POST /generate-image
```

## Recommended Algorithm

**Token Bucket**

## Why?

AI requests are expensive.

Users naturally send several requests while experimenting with prompts.

Token Bucket allows these small bursts without allowing continuous abuse.

---

# 6. File Upload APIs

## Business Requirement

Users may upload several files together.

```
Upload Image

Upload PDF

Upload Video
```

## Recommended Algorithm

**Token Bucket**

## Why?

Uploading multiple files is normal user behaviour.

Rejecting every burst would create a poor user experience.

Token Bucket provides enough flexibility while still enforcing limits.

---

# 7. Payment Processing

## Business Requirement

Protect payment providers from sudden spikes.

```
Checkout

↓

Payment Gateway

↓

Bank
```

## Recommended Algorithm

**Leaky Bucket**

## Why?

Payment systems benefit from a steady flow of requests.

Processing payments at a constant rate helps avoid sudden spikes that could overload downstream services.

---

# 8. Email Sending

## Business Requirement

Process outgoing emails gradually.

```
Email Queue

↓

SMTP Server

↓

Customer
```

## Recommended Algorithm

**Leaky Bucket**

## Why?

Email delivery usually isn't required within milliseconds.

A controlled processing rate is more important than immediate execution.

---

# 9. Notification Services

## Business Requirement

Deliver push notifications without overwhelming external providers.

```
Application

↓

Notification Queue

↓

Firebase

↓

Mobile Device
```

## Recommended Algorithm

**Leaky Bucket**

## Why?

Notification providers often have throughput limits.

Processing requests at a steady rate improves reliability.

---

# 10. Internal Microservices

## Business Requirement

Control traffic between services.

```
Service A

↓

Service B

↓

Service C
```

## Recommended Algorithm

**Sliding Window Counter**

## Why?

Internal services often generate very high request volumes.

Sliding Window Counter provides a good balance between:

- Accuracy
- Memory usage
- Performance

making it a practical choice for service-to-service communication.

---

# Decision Matrix

| Business Requirement | Recommended Algorithm | Why |
|----------------------|-----------------------|-----|
| OTP Verification | Fixed Window Counter | Simple request limits |
| Password Reset | Fixed Window Counter | Daily request limits |
| Login Protection | Sliding Window Log | Accurate rolling window |
| Public REST APIs | Token Bucket | Allows short bursts |
| AI APIs | Token Bucket | Controls expensive requests |
| File Upload APIs | Token Bucket | Better user experience |
| Payment Processing | Leaky Bucket | Constant processing rate |
| Email Sending | Leaky Bucket | Smooth outgoing traffic |
| Notification Services | Leaky Bucket | Protect downstream providers |
| Internal Microservices | Sliding Window Counter | Efficient at high traffic |

---

# A Practical Way to Choose

If I'm designing a new backend service, I usually ask myself these questions:

### Is the business rule simple?

Use **Fixed Window Counter**.

---

### Is fairness the highest priority?

Use **Sliding Window Log**.

---

### Do I need good accuracy with lower memory usage?

Use **Sliding Window Counter**.

---

### Should users be allowed to make a few requests quickly?

Use **Token Bucket**.

---

### Should requests be processed at a constant rate?

Use **Leaky Bucket**.

---

# Final Thoughts

One lesson I've learned over the years is that developers sometimes spend too much time trying to find the "best" rate limiting algorithm.

In practice, there usually isn't one.

A simple OTP service doesn't need the same solution as an AI platform.

A payment gateway has different requirements than a public REST API.

The best algorithm is the one that matches your application's behaviour while keeping the implementation as simple as possible.

Start by understanding the business requirement.

Understand the expected traffic pattern.

Then choose the algorithm that provides the right balance between simplicity, fairness, performance, and user experience.

That's exactly how rate limiting decisions are made in real-world backend systems.

---

# Repository Summary

In this repository, we covered:

- Why applications need rate limiting
- How Redis helps implement fast and scalable rate limiters
- Fixed Window Counter
- Sliding Window Log
- Sliding Window Counter
- Token Bucket
- Leaky Bucket
- Complete Python implementations for every algorithm
- Practical guidance for choosing the right algorithm

I hope this repository gives you a solid foundation for understanding how rate limiting works and helps you choose the right approach for your own backend applications.
