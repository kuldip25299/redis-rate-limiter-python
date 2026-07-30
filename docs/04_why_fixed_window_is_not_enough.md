# Why Fixed Window Isn't Always Enough

In the previous chapter, we implemented the **Fixed Window Counter**.

It's simple.

It's fast.

It uses very little memory.

For many applications, that's all you'll ever need.

So why do more advanced rate limiting algorithms exist?

The answer lies in one important limitation of the Fixed Window approach.

**The Burst Problem.**

---

# Let's Revisit Our Business Requirement

Suppose we're building an OTP service with the following rule.

> A user can request **5 OTPs per minute**.

At first glance, the Fixed Window algorithm appears to enforce this rule perfectly.

```
Limit

5 Requests

Per Minute
```

Every request increments a Redis counter.

When the counter reaches six, the request is rejected.

Simple.

But there's an important detail hidden in the words **"per minute."**

---

# A Timeline Tells the Real Story

Imagine our one-minute window starts at:

```
10:00:00
```

and ends at:

```
10:00:59
```

The user waits until the very end of the window before sending requests.

```
10:00:56  ✅ Request 1

10:00:57  ✅ Request 2

10:00:58  ✅ Request 3

10:00:59  ✅ Request 4

10:00:59  ✅ Request 5
```

The user has now reached the limit.

Everything looks correct.

---

# The Clock Changes

One second later...

```
10:01:00
```

The Fixed Window counter resets automatically.

Redis deletes the old key.

The application now believes the user has made:

```
0 Requests
```

So the user immediately sends:

```
10:01:00  ✅ Request 6

10:01:01  ✅ Request 7

10:01:02  ✅ Request 8

10:01:03  ✅ Request 9

10:01:04  ✅ Request 10
```

Every request is accepted.

---

# The Problem

Let's zoom out.

Within only a few seconds, the user has successfully sent:

```
★★★★★

Window 1

+

★★★★★

Window 2

=

10 Requests
```

Even though the configured limit was:

```
5 Requests Per Minute
```

The Fixed Window algorithm technically followed the rules.

But from the application's perspective, the traffic arrived in one sudden burst.

---

# Visual Timeline

```
Time
──────────────────────────────────────────────────────────>

10:00:56   ●

10:00:57   ●

10:00:58   ●

10:00:59   ● ●

================ Window Reset ================

10:01:00   ●

10:01:01   ●

10:01:02   ●

10:01:03   ●

10:01:04   ●
```

Ten requests were processed within a very short period.

---

# Why Is This Called the Burst Problem?

The requests are no longer evenly distributed across time.

Instead, they're concentrated around the boundary between two windows.

```
Normal Traffic

●     ●     ●     ●     ●

Burst Traffic

●●●●●●●●●●
```

The average request rate might still satisfy the configured limit, but the instantaneous load on the application increases significantly.

---

# Does Every Application Care?

Not necessarily.

Whether this behaviour is acceptable depends entirely on the business problem.

For many systems, occasional bursts are harmless.

Examples include:

- OTP verification
- Password reset
- Contact forms
- Email verification
- Internal administration tools

In these situations, keeping the implementation simple is often more valuable than achieving perfect request distribution.

---

# When Does It Become a Problem?

Other systems require traffic to be distributed more evenly.

For example:

- Public REST APIs
- AI inference services
- Payment gateways
- Stock market APIs
- Search platforms
- High-traffic SaaS applications

These systems are often designed around predictable request rates.

Allowing a sudden burst of traffic can increase latency, consume shared resources, or affect other users.

In those cases, the Fixed Window algorithm may no longer be the right choice.

---

# Can We Eliminate the Burst?

Yes.

Instead of grouping requests into fixed one-minute windows, we can evaluate requests using a continuously moving time window.

Rather than asking:

> "How many requests were made during this calendar minute?"

we ask:

> "How many requests have been made during the last 60 seconds?"

That small change makes a significant difference.

It removes the hard boundary between windows and prevents the burst behaviour we just observed.

---

# The Next Step

To answer this new question, storing only a single counter is no longer enough.

We now need to remember **when each request occurred.**

This leads us to the next algorithm:

**Sliding Window Log.**

Instead of storing just a counter, we'll store the timestamp of every request in Redis and evaluate only the requests that fall within the last 60 seconds.

It's slightly more complex than Fixed Window, but it provides much more accurate rate limiting.
