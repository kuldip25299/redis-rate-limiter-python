# Token Bucket

So far, every rate limiting algorithm we've explored has focused on **counting requests**.

- Fixed Window counted requests in a fixed time interval.
- Sliding Window Log counted requests in a rolling window.
- Sliding Window Counter estimated requests using weighted counters.

Although each algorithm works differently, they all answer the same question.

> **"How many requests has this user already made?"**

The Token Bucket algorithm approaches the problem from a different perspective.

Instead of counting past requests, it asks:

> **"Does the user currently have permission to make another request?"**

That permission is represented by **tokens**.

If a token is available, the request is allowed.

If there are no tokens left, the request is rejected.

This simple idea makes Token Bucket one of the most popular rate limiting algorithms used in production systems.

---

# A Real Business Problem

Imagine you're building an AI platform.

Users can call an API to generate text.

```
POST /generate-text
```

Some users send requests occasionally.

Others automate the API and generate hundreds of requests every minute.

Without any rate limiting:

```
User

↓

1000 Requests

↓

AI Model

↓

GPU Servers
```

The result?

- Expensive GPU usage
- Higher infrastructure costs
- Increased response times
- Poor experience for other users

We need a way to control request rates without making the API feel slow or restrictive.

---

# A Different Way to Think

Instead of counting requests every minute, imagine giving every user a small bucket.

```
      _________

     /         \

    |  Tokens   |

    |           |

    | ● ● ● ● ● |

     \_________/
```

Every token represents permission to make one request.

When a request arrives:

```
Request

↓

Take One Token

↓

Allow Request
```

If the bucket becomes empty:

```
Request

↓

No Tokens

↓

Reject Request
```

---

# Tokens Refill Automatically

The interesting part is that tokens don't stay empty forever.

They are added back over time.

For example:

```
Bucket Capacity

10 Tokens
```

Refill Rate

```
1 Token

Every Second
```

If the user waits:

```
5 Seconds
```

Five new tokens become available.

No manual reset.

No fixed window.

No rolling window.

The bucket simply refills continuously.

---

# Example

Suppose our configuration is:

```
Bucket Capacity

5 Tokens

Refill Rate

1 Token Every 10 Seconds
```

Initially:

```
★★★★★

5 Tokens
```

The user sends:

```
Request 1

↓

★★★★☆
```

Request 2

```
★★★☆☆
```

Request 3

```
★★☆☆☆
```

Request 4

```
★☆☆☆☆
```

Request 5

```
☆☆☆☆☆
```

The bucket is now empty.

Another request immediately arrives.

```
Request 6

↓

No Tokens

↓

Rejected
```

Now the user waits:

```
10 Seconds
```

Redis calculates that one new token should be added.

```
★☆☆☆☆
```

The next request is allowed.

---

# Why Is This Better?

Unlike Fixed Window, Token Bucket doesn't suddenly reset.

Unlike Sliding Window Log, it doesn't store every request.

Instead, it maintains only two pieces of information.

```
Current Tokens

Last Refill Time
```

Everything else is calculated when a request arrives.

---

# Redis Data Structure

A Redis Hash is sufficient.

```
Key

rate_limit:user:101

----------------------------

tokens

3

last_refill

1714557605
```

Only two values are stored.

Regardless of how many requests the user sends.

---

# Redis Commands Used

The implementation is surprisingly simple.

---

## HSET

Stores:

- Current token count
- Last refill timestamp

```
HSET
```

---

## HGETALL

Reads the current bucket state.

```
HGETALL
```

---

## EXPIRE

Automatically removes inactive users.

```
EXPIRE
```

---

# Request Processing Flow

```
             Request Arrives
                    │
                    ▼
        Read Bucket From Redis
                    │
                    ▼
      Calculate Tokens To Refill
                    │
                    ▼
       Update Current Token Count
                    │
         ┌──────────┴──────────┐
         │                     │
   Token Available        No Tokens
         │                     │
         ▼                     ▼
 Consume One Token      Reject Request
         │
         ▼
   Save Bucket State
```

Notice something important.

We never run a background job to refill tokens.

Instead, tokens are calculated **only when a request arrives**.

This makes the algorithm efficient and easy to scale.

---

# Why API Gateways Prefer Token Bucket

Imagine an application where users are usually idle but occasionally perform a burst of activity.

Examples include:

- Uploading several files
- Refreshing a dashboard
- Calling multiple APIs from a mobile app
- Loading data after login

A strict algorithm might reject these short bursts even though the average request rate is perfectly reasonable.

Token Bucket allows temporary bursts as long as enough tokens have accumulated.

This creates a much better user experience.

---

# Advantages

Token Bucket has several practical benefits.

- Allows short traffic bursts
- Smooth long-term request rate
- Very low memory usage
- Constant storage requirements
- Easy to implement with Redis
- Excellent for distributed systems
- No request timestamps required

---

# Limitations

Like every algorithm, Token Bucket has trade-offs.

- Slightly more complex than Fixed Window
- Requires refill calculations
- Choosing bucket size and refill rate requires tuning
- Incorrect configuration can make the API too restrictive or too permissive

The algorithm itself is simple.

Choosing good limits is usually the harder engineering problem.

---

# Common Use Cases

Token Bucket is widely used for:

- API gateways
- Reverse proxies
- AI APIs
- Public REST APIs
- Microservices
- SaaS platforms
- Cloud infrastructure
- Authentication services
- Developer platforms

Whenever short bursts are acceptable but sustained abuse should be prevented, Token Bucket is an excellent choice.

---

# Fixed Window vs Sliding Window vs Token Bucket

| Feature | Fixed Window | Sliding Window | Token Bucket |
|----------|--------------|----------------|--------------|
| Memory Usage | Very Low | Medium / High | Very Low |
| Burst Handling | Poor | Excellent | Excellent |
| Request Accuracy | Good | Excellent | Excellent |
| Stores Every Request | No | Sliding Window Log: Yes | No |
| Easy to Implement | Excellent | Moderate | Moderate |
| Production Usage | Common | Common | Very Common |

---

# A Practical Engineering Perspective

One of the reasons Token Bucket is so widely adopted is that it aligns well with how real users interact with applications.

People rarely send requests at a perfectly steady rate.

Instead, they work in bursts.

A user might open an application, trigger several API calls in quick succession, then remain idle for a while.

Token Bucket naturally accommodates this behaviour by allowing users to "save" unused capacity as tokens.

As long as the average request rate stays within the configured limit, the application remains responsive without sacrificing protection against abuse.

This balance between flexibility and control is what makes Token Bucket a popular choice in production environments.

---

# Summary

Token Bucket introduces a different way of thinking about rate limiting.

Instead of counting requests, it manages permission through tokens.

Every request consumes one token.

Tokens are automatically replenished over time based on a configured refill rate.

The result is a rate limiter that:

- Uses very little memory
- Supports temporary traffic bursts
- Maintains a predictable long-term request rate
- Scales well in distributed systems

In the next chapter, we'll implement the Token Bucket algorithm in Python using Redis and watch tokens being consumed and automatically refilled in real time.
