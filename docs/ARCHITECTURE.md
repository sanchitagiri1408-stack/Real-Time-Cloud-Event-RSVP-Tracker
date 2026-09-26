# Architecture

```text
                  Internet / Campus Network
                           |
                    React Web Frontend
                           |
                     HTTPS REST API
                           |
                      FastAPI Backend
                    /        |        \
             Auth/RBAC   Event Service   Analytics
                    \        |        /
                     PostgreSQL / SQLite
                           |
                    WebSocket Manager
                           |
                 Organizer Live Dashboard
```

## Cloud mapping

- SaaS: users consume the event platform through a browser.
- PaaS: a managed application host can run FastAPI and React.
- IaaS: a VM/container host is an optional deployment model.
- Managed database: PostgreSQL service replaces local SQLite.
- Real-time: WebSocket broadcasts RSVP changes.
- Serverless: the same domain logic can later be moved into functions.
- API gateway/load balancer/CDN/caching: production-scale deployment components described in `docs/SCALABILITY.md`.
- Secrets: environment variables; never commit `.env`.
- CI/CD: GitHub Actions example is provided.
