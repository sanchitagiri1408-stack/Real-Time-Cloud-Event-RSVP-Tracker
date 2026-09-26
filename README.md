# Real-Time Cloud-Based Event Planning & RSVP Tracker

A student-friendly, industry-oriented cloud computing project for event planning, RSVP management, live attendance tracking, authentication, analytics, notifications, and scalable architecture.

## Features

- Attendee and Organizer roles
- JWT authentication
- Event creation and management
- Going / Maybe / Not Going RSVP
- Duplicate RSVP prevention
- Capacity control and waitlist foundation
- Live WebSocket RSVP counters
- Organizer analytics
- Announcements and in-app notifications
- REST API
- SQLite local mode
- PostgreSQL cloud mode
- Docker support
- Automated API tests
- Cloud deployment architecture
- GitHub proof-building documentation

## Architecture

React -> FastAPI REST/WebSocket -> PostgreSQL (cloud) / SQLite (local)

See `docs/ARCHITECTURE.md`.

## Local setup

### Backend
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate
python -m pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

### Frontend
Open a second terminal:
```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Open the Vite URL shown in the terminal.

## Demo

1. Register an Organizer.
2. Create `Cloud Computing Workshop`, capacity 100.
3. Open another browser/incognito window.
4. Register an Attendee.
5. RSVP GOING.
6. Observe the organizer's live count.
7. Change MAYBE -> GOING and observe the count change without refresh.
8. Test unauthorized modification with an attendee account.
9. Use the test suite:
```bash
cd backend
pytest -q
```

## Docker

```bash
docker compose up --build
```

The compose file starts FastAPI and PostgreSQL. The React frontend can still run with Vite.

## Cloud deployment

For a free/student deployment, host the React frontend on a static frontend platform and FastAPI on a student-friendly container/PaaS provider, with PostgreSQL on a managed database provider. Set `DATABASE_URL`, `SECRET_KEY`, and `CORS_ORIGINS` as deployment environment variables. Free tiers and limits change, so verify the current provider plan before deployment.

## Cloud concepts demonstrated

Cloud computing, SaaS, PaaS, managed database, authentication, authorization, RBAC, REST APIs, WebSockets, event-driven updates, scalability, elasticity, load balancing, caching, environment variables, secrets management, logging, monitoring, backup, CI/CD, and deployment.

## Important concurrency note

The local reference implementation demonstrates the race-condition problem and keeps the code beginner-friendly. For a production PostgreSQL deployment, capacity enforcement must use a transaction/row lock or atomic conditional update. See `docs/SCALABILITY.md`.

## Security

Never commit `.env`, cloud credentials, passwords, or API keys. The frontend must never be trusted for RSVP counts; the backend/database is the source of truth.

## Screenshots

Use the filenames in `docs/PROOF_CHECKLIST.md`.

## Project report

See `docs/REPORT.md`.

## Interview preparation

See `docs/INTERVIEW.md`.

## License

Educational project; add your preferred open-source license before public release.
