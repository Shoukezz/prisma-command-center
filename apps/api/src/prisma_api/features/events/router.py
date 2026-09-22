from fastapi import APIRouter, Query

from prisma_api.core.deps import DbSession
from prisma_api.features.events.presentation import event_to_player_schema as event_to_schema
from prisma_api.features.world.schemas import EventSchema
from prisma_api.features.world.simulation import WorldSimulationService

router = APIRouter()


@router.get("", response_model=list[EventSchema])
def list_events(
    db: DbSession,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[EventSchema]:
    service = WorldSimulationService(db)
    return [event_to_schema(e) for e in service.list_events(limit=limit)]
