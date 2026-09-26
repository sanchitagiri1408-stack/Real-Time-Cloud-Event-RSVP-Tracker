# Project Report — Real-Time Cloud-Based Event Planning & RSVP Tracker

## Abstract
This project implements a real-time event planning and RSVP platform demonstrating cloud computing concepts through a browser-based multi-user application. Organizers create and manage events, while attendees discover events and submit Going, Maybe, or Not Going responses. RSVP changes are broadcast over WebSockets so organizer dashboards can update without manual refresh.

## Introduction
Manual event coordination often relies on spreadsheets, messages, and delayed attendance updates. A centralized cloud application provides shared access, controlled permissions, automated notifications, and live analytics.

## Problem Statement
Traditional event coordination can suffer from duplicate responses, stale attendance counts, difficult capacity management, and limited visibility for organizers.

## Objectives
- Build a cloud-ready event management application.
- Demonstrate REST APIs and authentication.
- Provide real-time RSVP updates.
- Enforce role-based authorization.
- Demonstrate capacity and concurrency concepts.
- Provide analytics, notifications, testing, and deployment documentation.

## Existing System
Manual spreadsheets and messaging tools can work for small events but require repeated coordination and do not inherently provide application-level authorization or real-time capacity control.

## Proposed System
A React frontend communicates with FastAPI REST endpoints. PostgreSQL can be used as the managed cloud database. WebSockets distribute RSVP updates to connected clients.

## Cloud Computing Concepts
SaaS is represented by browser-based consumption. PaaS is represented by managed application hosting. A managed PostgreSQL service provides database-as-a-service. Environment variables represent secrets configuration. Horizontal scaling, load balancing, CDN, caching, monitoring, and queues are documented as production extensions.

## Real-Time Computing
The WebSocket channel is subscribed to an event. When an RSVP changes, the backend recalculates counts and broadcasts an `RSVP_UPDATED` message. Connected dashboards update immediately.

## Security
Passwords are hashed. API routes require bearer tokens. Organizer routes enforce role checks and event ownership. CORS is configured through environment variables. Secrets are excluded from Git.

## Testing
Automated API tests cover health, registration, duplicate registration, event creation, and RSVP behavior. The test plan additionally covers capacity, authorization, realtime failure, and concurrency.

## Limitations
The reference implementation is intentionally student-friendly. SQLite does not provide the same locking/concurrency behavior as PostgreSQL. For production capacity safety, use a PostgreSQL transaction or atomic conditional update. Email/SMS/push are documented as optional integrations.

## Future Scope
Managed authentication, managed realtime services, Redis/pub-sub, asynchronous notification workers, observability, CI/CD, waitlist promotion workers, and richer analytics can be added.

## Conclusion
The project combines event management with cloud-oriented architecture, REST services, authentication, role-based authorization, realtime communication, database design, concurrency reasoning, testing, security, and deployment.
