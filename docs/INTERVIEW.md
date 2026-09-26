# 10 interview questions and strong answers

## 1. Explain your project.
I built a real-time cloud-based event planning and RSVP tracker. Organizers create events and monitor attendance, while attendees register and choose Going, Maybe, or Not Going. FastAPI exposes REST APIs, the database stores users/events/RSVPs, JWT authentication protects APIs, and WebSockets broadcast RSVP changes to connected dashboards without manual refresh.

## 2. Why did you use cloud computing?
The project needs centralized storage and access from different devices. Cloud deployment also makes it possible to scale application instances and use managed databases instead of maintaining infrastructure locally.

## 3. How does real-time communication work?
The browser opens a WebSocket for an event. After a successful RSVP, the backend recalculates the event counts and broadcasts an `RSVP_UPDATED` message. The organizer dashboard receives it and updates its counters.

## 4. Why use a relational database?
Users, events and RSVPs have clear relationships. A relational database supports foreign keys and a unique `(event_id, user_id)` constraint, which helps prevent duplicate active RSVP records.

## 5. How are REST APIs used?
The frontend calls REST endpoints for registration, login, event CRUD, RSVP operations, analytics, announcements, and notifications. HTTP methods express the intended operation and status codes communicate success or failure.

## 6. How does authentication differ from authorization?
Authentication identifies the user after login. Authorization checks what that user is allowed to do. For example, an attendee can RSVP, but only an organizer can create or modify their own event.

## 7. How do you prevent a capacity race condition?
A naive read-then-insert sequence can accept two final-seat requests simultaneously. In a production PostgreSQL deployment I would perform the capacity check and write inside one transaction with row locking or an atomic conditional update.

## 8. How would you scale it?
I would keep API instances stateless, put them behind a load balancer, use managed PostgreSQL with pooling, add caching, queue notifications, and use Redis/pub/sub or a managed realtime service for WebSocket fan-out.

## 9. What security controls did you implement?
Passwords are hashed, JWTs protect APIs, roles are checked on protected routes, event ownership is verified, CORS is configurable, secrets use environment variables, and the backend remains the source of truth for RSVP counts.

## 10. What happens if realtime disconnects?
The application should treat WebSocket delivery as an enhancement rather than the source of truth. REST/database state remains authoritative. A production frontend can reconnect automatically and fetch the current event state after reconnection.
