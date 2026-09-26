# Scalability and concurrency

At 100 users, one application instance and a managed relational database are sufficient for a student demonstration.

At 10,000 users, use a load balancer, multiple stateless API instances, managed PostgreSQL, connection pooling, Redis caching, and a shared pub/sub layer for WebSocket fan-out.

At 1,000,000 users or a burst of 100,000 RSVP attempts in five minutes, protect the RSVP endpoint with rate limiting and a queue. Use database transactions/conditional updates for capacity, partition or shard high-volume data when necessary, and move notifications to asynchronous workers.

## Race condition

A naive sequence:

1. Read `currentGoing`.
2. Check `currentGoing < capacity`.
3. Insert RSVP.

Two requests can both read 99 when capacity is 100, then both insert.

For a production PostgreSQL implementation, the final-seat operation should be one atomic transaction, for example by locking the event row (`SELECT ... FOR UPDATE`) before counting/updating, or by using a conditional atomic update. The local reference implementation keeps the logic understandable and explicitly documents this boundary so the student can explain it in an interview.

WebSocket servers should be stateless behind a load balancer with Redis/pub/sub or a managed realtime service when multiple instances are used.
