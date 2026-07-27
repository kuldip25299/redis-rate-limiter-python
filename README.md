# Redis Rate Limiter using Python

I've come across many Rate Limiting implementations that show the code but skip the engineering decisions behind it. This repository is my attempt to bridge that gap by implementing each algorithm from scratch using Python and Redis, while explaining where it fits—and where it doesn't.

Most articles about Rate Limiting focus on the algorithm itself.

They explain **Fixed Window**, **Token Bucket**, or **Sliding Window**, followed by a few lines of code using `INCR` and `EXPIRE`.

What they rarely explain is **why these algorithms exist**, **what problem each one solves**, and **when one approach becomes a poor choice for a production system**.

After working on backend systems, one thing became clear:

> Choosing the wrong Rate Limiting algorithm is rarely a correctness problem—it's usually a scalability problem.

An OTP service, a payment gateway, a public REST API, and an AI inference endpoint all require Rate Limiting, but they don't necessarily require the same algorithm.

A Fixed Window Counter may be perfectly acceptable for one workload, while another system benefits from a Token Bucket because it needs to absorb short traffic bursts without rejecting legitimate users.

This repository was created to explain those trade-offs through simple Python implementations backed by Redis.

The goal is not to build another Rate Limiting library.

The goal is to understand **how these algorithms work**, **why Redis is commonly used**, and **how to implement each approach from scratch**.

Every implementation is intentionally small, fully runnable, and focuses on one idea at a time.

No frameworks.

No unnecessary abstractions.

No hidden magic.

Just the algorithm, Redis, and Python.

---

# What You'll Find

Instead of covering only the "happy path", each algorithm is explained from an engineering perspective.

Every chapter follows the same structure:

- The business problem
- Why Rate Limiting is required
- Why Redis is a good fit
- How the algorithm works internally
- Complete Python implementation
- Advantages
- Limitations
- Typical production use cases

The emphasis is on understanding the reasoning behind each design rather than simply copying code.

---

# Algorithms Covered

- Fixed Window Counter
- Sliding Window Log
- Sliding Window Counter
- Token Bucket
- Leaky Bucket

Each implementation is independent, allowing you to study one algorithm at a time without relying on a large framework or shared infrastructure.

---

# Why Redis?

Redis has become the default choice for distributed Rate Limiting because it offers exactly the primitives these algorithms need:

- Atomic counters
- Key expiration (TTL)
- Fast in-memory operations
- Sorted Sets for timestamp-based algorithms
- Consistent performance under high request volumes

Throughout this repository, you'll see not only **which Redis commands are used**, but also **why they're chosen**.

---

# Repository Structure

```text
docs/
    01_what_is_rate_limiting.md
    02_why_redis.md
    03_fixed_window.md
    04_sliding_window_log.md
    05_sliding_window_counter.md
    06_token_bucket.md
    07_leaky_bucket.md
    08_algorithm_comparison.md
    09_real_world_examples.md

examples/
    fixed_window.py
    sliding_window_log.py
    sliding_window_counter.py
    token_bucket.py
    leaky_bucket.py
```

---

# Who Is This Repository For?

This repository is aimed at developers who want to move beyond copy-pasting Rate Limiting examples and understand the engineering decisions behind them.

Whether you're preparing for backend interviews, designing APIs, or simply curious about how production systems protect themselves from abuse, the examples here are designed to be practical, concise, and easy to experiment with.

---

If this repository helps you understand Rate Limiting a little better, consider giving it a ⭐.
