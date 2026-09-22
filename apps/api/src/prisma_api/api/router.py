from fastapi import APIRouter

from prisma_api.features.analysts.router import router as analysts_router
from prisma_api.features.auth.router import router as auth_router
from prisma_api.features.events.router import router as events_router
from prisma_api.features.game_session.router import router as game_session_router
from prisma_api.features.health.router import router as health_router
from prisma_api.features.intelligence.router import router as intelligence_router
from prisma_api.features.operations.router import router as operations_router
from prisma_api.features.world.router import router as world_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(world_router, prefix="/world", tags=["world"])
api_router.include_router(events_router, prefix="/events", tags=["events"])
api_router.include_router(intelligence_router, prefix="/intelligence", tags=["intelligence"])
api_router.include_router(analysts_router, prefix="/analysts", tags=["analysts"])
api_router.include_router(operations_router, prefix="/operations", tags=["operations"])
api_router.include_router(game_session_router, prefix="/sessions", tags=["game-session"])
