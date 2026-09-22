# Technical Architecture

## Principles

- **Local development only** — run the API and web app on the developer machine.
- **Single-player prototype** — no authentication or multi-user/session isolation is
  implemented; do not expose the API to a network.
- **No containerization** — no Docker, Docker Compose, or Kubernetes.
- **Single-process backend** — SQLite and in-process background work (no Redis, Celery, or external job queue).

## Frontend

- Next.js (App Router)
- TypeScript
- React
- Zustand (UI state)
- TanStack React Query (server state)
- Tailwind CSS
- Leaflet (strategic map)

## Backend

- FastAPI
- SQLAlchemy 2
- Pydantic / pydantic-settings
- Alembic (migrations)
- Uvicorn (local ASGI server)

## Database

- **SQLite** — file at `apps/api/data/prisma.db`
- One writer per API process; suitable for single-player local sessions
- Migrations via Alembic; `create_all` only for local bootstrap if needed

## Realtime

- WebSockets (FastAPI) for live feeds (events, operations, intel)
- No message broker; connections managed in-process

## Background work

- World ticks, operation resolution, and event generation run **in-process** via an `asyncio` task started in the FastAPI lifespan
- No Celery, Redis, or separate worker process required for local development

## Repository layout

```
apps/web/              Next.js frontend
apps/api/              FastAPI backend
packages/shared/       Shared TypeScript types and API constants
docs/                  Design documentation
rules/                 Cursor rules
```

## Architecture style

- Feature-based modules (`features/auth`, `features/world`, …)
- Domain-driven design boundaries per game system
- Service layer (business logic)
- Repository layer (persistence)
- API routers thin; no gameplay logic in HTTP handlers

## Local run

| Service | Command | URL |
|---------|---------|-----|
| API | `npm run dev:api` | http://localhost:8000 |
| Web | `npm run dev:web` | http://localhost:3000 |
| API docs | — | http://localhost:8000/docs |

## Explicit exclusions

Do not introduce:

- Docker / Docker Compose / Kubernetes
- PostgreSQL, Redis, Celery
- External job queues or cache servers for core gameplay
