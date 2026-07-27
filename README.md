# Redis Rate Limiter using Python

> Learn how Rate Limiting works, why Redis is widely used for it, and build different Rate Limiting algorithms in Python with simple, practical examples.

---

## 📖 About This Repository

Rate Limiting is one of the most common techniques used in modern backend systems to protect applications from abuse, prevent server overload, and ensure fair usage of resources.

Whether you're building a login system, an OTP service, a payment gateway, or a public REST API, chances are you'll need some form of Rate Limiting.

In this repository, you'll learn:

- What Rate Limiting is
- Why applications need it
- Why Redis is commonly used
- Different Rate Limiting algorithms
- How each algorithm works internally
- Complete Python implementations
- Advantages and limitations of each approach
- Real-world use cases

Every implementation is intentionally kept simple so you can understand the core concepts without unnecessary complexity.

---

# 🎯 Who Is This Repository For?

This repository is suitable for:

- Beginners learning Redis
- Python Developers
- Backend Developers
- Full Stack Developers
- Developers preparing for system design interviews
- Anyone curious about how Rate Limiting works

---

# 🚀 What You Will Learn

By the end of this repository, you'll understand:

- Why Rate Limiting is important
- How Redis helps implement Rate Limiting
- Different Rate Limiting algorithms
- Which Redis data structures are used
- When to choose each algorithm
- How to build your own Rate Limiter in Python

---

# 📚 Repository Structure

```
redis-rate-limiter-using-python/

│
├── README.md
│
├── docs/
│   ├── 01_what_is_rate_limiting.md
│   ├── 02_why_redis.md
│   ├── 03_fixed_window.md
│   ├── 04_sliding_window_log.md
│   ├── 05_sliding_window_counter.md
│   ├── 06_token_bucket.md
│   ├── 07_leaky_bucket.md
│   ├── 08_algorithm_comparison.md
│   └── 09_real_world_examples.md
│
├── examples/
│   ├── fixed_window.py
│   ├── sliding_window_log.py
│   ├── sliding_window_counter.py
│   ├── token_bucket.py
│   └── leaky_bucket.py
│
├── requirements.txt
└── docker-compose.yml
```

---

# 📖 Learning Path

We recommend reading the chapters in the following order.

| Chapter | Topic |
|----------|-------|
| 01 | What is Rate Limiting? |
| 02 | Why Redis? |
| 03 | Fixed Window Counter |
| 04 | Sliding Window Log |
| 05 | Sliding Window Counter |
| 06 | Token Bucket |
| 07 | Leaky Bucket |
| 08 | Algorithm Comparison |
| 09 | Real World Examples |

Each chapter includes:

- Business Problem
- Simple Explanation
- Redis Commands Used
- Redis Data Structure
- Python Implementation
- Advantages
- Limitations
- When to Use

---

# 🌍 Real-World Examples

Throughout this repository, we'll solve problems commonly found in production systems.

Examples include:

- OTP Verification
- Login Protection
- Password Reset APIs
- Public REST APIs
- AI APIs
- Payment APIs
- File Upload APIs
- Search APIs

These examples will help you understand where each algorithm fits best.

---

# 💻 Prerequisites

Basic knowledge of:

- Python
- APIs
- HTTP Requests

No prior Redis knowledge is required.

---

# ⚙️ Technologies Used

- Python 3.12+
- Redis 7+
- redis-py

---

# 📦 Installation

## 1. Clone the repository

```bash
git clone https://github.com/<your-username>/redis-rate-limiter-using-python.git

cd redis-rate-limiter-using-python
```

---

## 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Start Redis

If Redis is already installed:

```bash
redis-server
```

Or using Docker:

```bash
docker compose up -d
```

---

# ▶️ Running Examples

Every algorithm has its own standalone Python file.

Example:

```bash
python examples/fixed_window.py
```

No additional configuration is required.

---

# 🧠 Algorithms Covered

## 1. Fixed Window Counter

The simplest Rate Limiting algorithm.

Uses a Redis counter that resets after a fixed time window.

---

## 2. Sliding Window Log

Stores every request timestamp to provide more accurate Rate Limiting.

---

## 3. Sliding Window Counter

An optimized version of Sliding Window Log that uses less memory while maintaining good accuracy.

---

## 4. Token Bucket

Allows occasional bursts of traffic while maintaining a controlled average request rate.

One of the most widely used algorithms in modern APIs.

---

## 5. Leaky Bucket

Processes requests at a constant rate, smoothing out traffic spikes.

Commonly used in networking and traffic shaping.

---

# 📊 Algorithm Comparison

At the end of this repository, we'll compare all algorithms based on:

- Accuracy
- Memory Usage
- Performance
- Burst Handling
- Complexity
- Typical Use Cases

This will help you choose the right algorithm for your application.

---

# 🎯 Repository Goals

This repository focuses on learning through practical examples.

Our goals are to:

- Explain concepts simply
- Build working Python implementations
- Use Redis effectively
- Keep code clean and readable
- Avoid unnecessary complexity
- Help developers understand the "why" behind each algorithm

---

# 🤝 Contributions

Contributions are welcome!

If you find a bug, have an improvement, or want to add another example, feel free to open an issue or submit a pull request.

---

# ⭐ Support

If you find this repository helpful:

- Star the repository
- Share it with other developers
- Follow along as new algorithms and examples are added

Happy Learning! 🚀
