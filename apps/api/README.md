# PRISMA API

FastAPI backend with feature-based modules under `src/prisma_api/features/`.

Runs **locally** with SQLite. No Docker, Redis, Celery, or PostgreSQL.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../../.env.example .env
mkdir -p data
```

From repository root:

```bash
npm run install:api
npm run dev:api
```

## Layout

- `core/` — configuration, database, scheduler, dependencies
- `features/` — domain features (auth, world, events, game_session)
- `models/` — SQLAlchemy models (Phase 1)
- `alembic/` — database migrations
- `data/` — SQLite database file (gitignored)

## Tests

```bash
PYTHONPATH=src .venv/bin/pytest
# or from repo root:
npm run test:api
```
