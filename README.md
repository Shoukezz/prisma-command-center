# PRISMA Command Center

Monorepo for the PRISMA strategic command center simulator. See `/docs` for design documentation.

This is a local, single-player development build. It does not provide user
accounts or access control and must not be exposed beyond the local machine.

## Structure

```
apps/web/          Next.js frontend (TypeScript, Tailwind)
apps/api/          FastAPI backend (SQLAlchemy, SQLite)
packages/shared/   Shared TypeScript types and constants
```

## Prerequisites

- Node.js 20+
- Python 3.9+
- npm

## Quick start (local)

```bash
# Install frontend workspaces
npm install

# API virtualenv and dependencies
npm run install:api

# Environment (optional; defaults work for local dev)
cp .env.example .env
cp .env.example apps/api/.env
mkdir -p apps/api/data

# Database migrations (when migrations exist)
cd apps/api && .venv/bin/alembic upgrade head

# Terminal 1 — API
npm run dev:api

# Terminal 2 — Web
npm run dev:web
```

- Web: http://localhost:3000
- API: http://localhost:8000
- API docs: http://localhost:8000/docs

The world advances automatically every 15 seconds while it is running. Change
`TICK_INTERVAL_SECONDS` locally to tune the real-time cadence; pause and speed
controls are persisted with the active world.

## Scripts

| Script | Description |
|--------|-------------|
| `npm run dev:web` | Next.js dev server |
| `npm run dev:api` | FastAPI with hot reload |
| `npm run install:api` | Create venv and install Python deps |
| `npm run test:api` | Run API tests |
| `npm run build:web` | Production build of frontend |
| `npm run lint:web` | ESLint on frontend |

## API tests

```bash
npm run test:api
```
