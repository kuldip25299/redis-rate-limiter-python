# Leaky Bucket

In the previous chapter, we explored the **Token Bucket** algorithm.

Token Bucket allows users to accumulate unused capacity as tokens.

When enough tokens are available, users can send multiple requests in a short period of time.

For many applications, this is exactly the desired behaviour.

For example:

- Loading a dashboard
- Uploading multiple files
- Making several API calls after login

Short bursts improve the user experience while still enforcing a long-term request rate.

However, not every system wants burst traffic.

Some systems require requests to arrive at a **steady, predictable rate**.

That's where the **Leaky Bucket** algorithm becomes useful.

---

# A Real Business Problem

Imagine you're building a payment processing system.

Thousands of clients submit payment requests.

```
Client A

↓

100 Requests

↓

Payment Service
```

If all 100 requests arrive at the same time:

- CPU usage spikes
- Database connections increase
- Queue sizes grow
- Response times become unpredictable

Even if the system can eventually process all requests, handling sudden bursts is inefficient.

Instead, we want requests to arrive gradually.

---

# A Different Way to Think

Imagine a bucket filled with water.

```
      _________

     /         \

    |~~~~~~~~~~~|

    |~~~~~~~~~~~|

    |~~~~~~~~~~~|

     \_________/

          |

          |

         \|/

       Water Drips
```

Water enters the bucket at different speeds.

Sometimes slowly.

Sometimes very quickly.

But the bucket always leaks water at a constant rate.

The outgoing flow never changes.

That's exactly how the Leaky Bucket algorithm works.

Incoming requests may arrive in bursts, but requests leave the bucket at a fixed rate.

---

# How It Works

Think of the bucket as a queue.

```
Incoming Requests

↓

[ Request Queue ]

↓

Process One Request

↓

Process One Request

↓

Process One Request
```

Requests enter the queue immediately.

The application processes them one by one at a constant rate.

If the queue becomes full:

```
Incoming Request

↓

Queue Full

↓

Reject Request
```

Unlike Token Bucket, requests are not executed immediately simply because capacity exists.

Instead, they wait their turn.

---

# Token Bucket vs Leaky Bucket

Although the names sound similar, they solve different problems.

### Token Bucket

```
★★★★★

Consume Tokens

Burst Allowed
```

If enough tokens are available, several requests can be processed immediately.

---

### Leaky Bucket

```
██████████

↓

↓

↓

↓

Constant Output
```

Requests are released at a fixed speed regardless of how quickly they arrive.

---

# Redis Data Structure

A Redis List is a simple choice for implementing the queue.

```
Key

request_queue:user:101

--------------------------

Request 1

Request 2

Request 3

Request 4
```

New requests are added to the end of the queue.

Processed requests are removed from the front.

---

# Redis Commands Used

The Leaky Bucket implementation uses only a few Redis commands.

### RPUSH

Add a request to the end of the queue.

```
RPUSH
```

---

### LPOP

Remove the oldest request.

```
LPOP
```

---

### LLEN

Check how many requests are waiting.

```
LLEN
```

---

### EXPIRE

Automatically clean up inactive queues.

```
EXPIRE
```

---

# Request Processing Flow

```
          New Request
               │
               ▼
        Is Queue Full?
         ┌─────┴─────┐
         │           │
       No            Yes
         │           │
         ▼           ▼
 Add To Queue     Reject Request
         │
         ▼
Wait For Processing
         │
         ▼
Remove Oldest Request
         │
         ▼
Process Request
```

The key idea is simple.

Incoming traffic can vary.

Outgoing traffic remains constant.

---

# Why Is This Useful?

Many backend services perform expensive work.

Examples include:

- Sending emails
- Processing payments
- Image conversion
- Video transcoding
- PDF generation
- Database imports

Allowing thousands of requests to execute simultaneously can overwhelm downstream systems.

Leaky Bucket smooths the workload and protects these services.

---

# Advantages

The Leaky Bucket algorithm provides several practical benefits.

- Produces a constant processing rate
- Smooths burst traffic
- Protects downstream services
- Easy to understand
- Predictable system load
- Simple Redis implementation

---

# Limitations

Like every algorithm, it has trade-offs.

- Requests may wait before processing
- Queue size must be limited
- Increased latency during heavy traffic
- Not suitable when users expect immediate responses

Unlike Token Bucket, Leaky Bucket prioritizes stability over responsiveness.

---

# Common Use Cases

Leaky Bucket is commonly used for:

- Payment processing
- Email delivery systems
- Notification services
- Background job queues
- Video processing
- File uploads
- Database synchronization
- Traffic shaping in networking

Whenever downstream services require a steady request rate, Leaky Bucket is an excellent choice.

---

# Token Bucket vs Leaky Bucket

| Feature | Token Bucket | Leaky Bucket |
|---------|--------------|--------------|
| Allows Bursts | Yes | No |
| Output Rate | Variable | Constant |
| User Experience | More Responsive | More Predictable |
| Queue Required | No | Yes |
| Memory Usage | Very Low | Low |
| Primary Goal | Control Request Rate | Smooth Request Flow |

---

# Engineering Notes

One lesson I've learned while building backend systems is that developers often confuse Token Bucket and Leaky Bucket because of their names.

The algorithms are actually solving different problems.

If your application benefits from allowing users to perform several actions quickly—for example, opening a dashboard or making multiple API calls after login—Token Bucket is usually the better choice.

If your goal is to protect a downstream service by ensuring requests are processed at a constant pace, Leaky Bucket is often the better option.

The choice isn't about which algorithm is "better."

It's about which behaviour best matches your system's requirements.

---

# Summary

Leaky Bucket approaches rate limiting differently from the algorithms we've studied so far.

Instead of deciding whether a request is allowed immediately, it controls **how quickly requests are processed**.

Requests may arrive in bursts, but they leave the system at a steady, predictable rate.

This makes Leaky Bucket an excellent choice for systems that need to protect downstream resources from sudden traffic spikes.

In the next chapter, we'll build a complete Python implementation using Redis and simulate requests entering and leaving the bucket in real time.
