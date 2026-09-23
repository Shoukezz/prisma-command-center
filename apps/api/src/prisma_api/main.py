import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from prisma_api.api.router import api_router
from prisma_api.api.websocket import broadcast_world_update
from prisma_api.api.websocket import router as websocket_router
from prisma_api.core.config import get_settings
from prisma_api.core.database import SessionLocal, init_db
from prisma_api.core.scheduler import BackgroundScheduler
from prisma_api.features.world.seed import ensure_world
from prisma_api.features.world.simulation import WorldSimulationService

_scheduler = BackgroundScheduler()
logger = logging.getLogger(__name__)


async def _run_world_ticks() -> None:
    """Advance the local single-player world while it is running."""
    settings = get_settings()
    while True:
        db = SessionLocal()
        try:
            simulation = WorldSimulationService(db)
            world = simulation.get_active_world()
            if world.is_paused:
                await asyncio.sleep(min(settings.tick_interval_seconds, 1.0))
                continue
            interval = settings.tick_interval_seconds / world.speed
        except Exception:
            db.rollback()
            logger.exception("Could not read world tick state")
            await asyncio.sleep(settings.tick_interval_seconds)
            continue
        finally:
            db.close()

        await asyncio.sleep(interval)
        db = SessionLocal()
        try:
            simulation = WorldSimulationService(db)
            world = simulation.get_active_world()
            if world.is_paused:
                continue
            result = simulation.run_single_tick(world)
            await broadcast_world_update(
                "world.tick",
                {
                    "world_id": result.world.id,
                    "game_minutes": result.world.game_minutes,
                    "ticks_elapsed": result.world.ticks_elapsed,
                },
            )
        except Exception:
            db.rollback()
            logger.exception("World tick failed")
        finally:
            db.close()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    init_db()
    db = SessionLocal()
    try:
        ensure_world(db)
    finally:
        db.close()
    settings = get_settings()
    if settings.auto_tick and settings.environment != "test":
        _scheduler.start(_run_world_ticks)
    yield
    await _scheduler.shutdown()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_prefix)
    app.include_router(websocket_router)

    return app


app = create_app()
