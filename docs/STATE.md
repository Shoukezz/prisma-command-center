# Verified Build & Test State

Last verified: 2026-09-22, on macOS (Node v26.9.0, Python 3.14.7).

`MVP_AUDIT_REPORT.md` is a **historical snapshot from 2026-05-31**. It is not
re-run automatically and its numbers (test counts, DB row counts) are frozen
at that date. This file replaces it as the source of truth for "does it
actually work right now."

## Results

| Command | Result | Notes |
|---|---|---|
| `npm install` | ✅ pass | 369 packages, 0 install errors. 6 `npm audit` advisories (5 high, 1 critical) not yet triaged — carried into a later step, not this one. |
| `npm run install:api` | ✅ pass | Spec expected py3.12 on a py3.9 system; this machine has **Python 3.14.7** and neither constraint applied. `pyproject.toml` requires `>=3.9`, so 3.14 satisfies it. No compatibility issues hit. |
| `npm run test:api` | ✅ pass | **18/18 tests passed** (audit report claimed 15/15 — count has drifted since May, in a good direction). Two deprecation warnings only (`httpx`/starlette TestClient, `anyio.abc.BlockingPortal`), no failures. |
| `npm run build:web` | ✅ pass | Next.js 16.2.12 (Turbopack), 8 static routes generated, TypeScript check embedded in the build succeeded. |
| `npm run typecheck:web` | ✅ pass | `tsc --noEmit` clean, no errors. |
| `npm run lint:web` | ❌ **fails** | 2 real errors in `apps/web/src/features/command-center/components/onboarding-guide.tsx`: a `setState` call inside a `useEffect` body (react-hooks/set-state-in-effect) and a ref read during render (react-hooks/refs), both at lines 123 and 152. Not caught by `build:web` because Next's production build does not run this eslint config the same way. |
| `apps/api` — `ruff check src` | ❌ **fails** | 106 lint errors, mostly `F821 Undefined name` on SQLAlchemy `Mapped[list["X"]]` forward references in `src/prisma_api/models/world.py` and related model files (relationship target classes referenced as strings but not imported for ruff to resolve). 57 are auto-fixable with `ruff --fix`. Did not run pytest at all — the two are independent and pytest is unaffected. |

## What this means for the roadmap

- The API test suite and the web build/typecheck are genuinely green — the
  audit's "MVP operational" claim is confirmed as still true today, not just
  inherited from May.
- Two things the audit didn't measure at all: `eslint` (web) and `ruff`
  (api) were never run as part of that report. Both fail today. Fixing them
  is in scope for step 2 (`fix: <whatever step 1 surfaced>`) rather than this
  step.
- `npm audit` vulnerabilities are noted but not triaged; revisit before the
  CI step (step 4) locks in a baseline.

## Router / test coverage snapshot

Feature routers under `apps/api/src/prisma_api/features/`: `analysts`,
`auth`, `events`, `game_session`, `health`, `intelligence`, `operations`,
`world`.

Existing test files: `test_analysts.py`, `test_health.py`,
`test_intelligence.py`, `test_intelligence_actions.py`,
`test_operations.py`, `test_world_simulation.py`.

No dedicated tests for `auth`, `events`, or `game_session` routers yet.
There is no `diplomacy` feature module in the API — the web app's
`/diplomacy` route exists as a page but has no backing router; this needs
confirming in step 2 before writing tests for it.
