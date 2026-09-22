from fastapi import APIRouter

from prisma_api.api.websocket import broadcast_world_update
from prisma_api.core.deps import DbSession
from prisma_api.features.intelligence.enrichment import build_intel_schemas
from prisma_api.features.operations.mappers import asset_to_schema, operation_to_schema
from prisma_api.features.operations.service import OperationsService
from prisma_api.features.world.mappers import (
    clock_to_schema,
    event_to_schema,
    geography_to_schema,
    world_state_to_schema,
)
from prisma_api.features.world.schemas import (
    AdvanceResultSchema,
    AdvanceTimeSchema,
    ClockUpdateSchema,
    GeographySchema,
    WorldStateSchema,
)
from prisma_api.features.world.seed import reset_world
from prisma_api.features.world.simulation import WorldSimulationService

router = APIRouter()


def _full_state(db: DbSession, service: WorldSimulationService) -> WorldStateSchema:
    world = service.get_active_world()
    ops = OperationsService(db)
    intel = service.list_intel()
    return world_state_to_schema(
        world,
        service.list_events(),
        build_intel_schemas(db, intel),
        ops.list_assets(),
        ops.list_operations(),
    )


@router.get("/state", response_model=WorldStateSchema)
def get_world_state(db: DbSession) -> WorldStateSchema:
    service = WorldSimulationService(db)
    return _full_state(db, service)


@router.get("/geography", response_model=GeographySchema)
def get_geography(db: DbSession) -> GeographySchema:
    service = WorldSimulationService(db)
    world = service.get_world_with_geography()
    return geography_to_schema(world)


@router.post("/reset", response_model=WorldStateSchema)
async def reset_game_world(db: DbSession) -> WorldStateSchema:
    reset_world(db)
    service = WorldSimulationService(db)
    state = _full_state(db, service)
    await broadcast_world_update("world.updated", state.model_dump(mode="json"))
    return state


@router.patch("/clock", response_model=WorldStateSchema)
async def update_clock(payload: ClockUpdateSchema, db: DbSession) -> WorldStateSchema:
    service = WorldSimulationService(db)
    service.update_clock(is_paused=payload.is_paused, speed=payload.speed)
    state = _full_state(db, service)
    await broadcast_world_update("world.updated", state.model_dump(mode="json"))
    return state


@router.post("/tick", response_model=AdvanceResultSchema)
async def run_tick(db: DbSession) -> AdvanceResultSchema:
    service = WorldSimulationService(db)
    result = service.run_single_tick()
    ops = OperationsService(db)
    response = AdvanceResultSchema(
        clock=clock_to_schema(result.world),
        ticks_run=result.ticks_run,
        new_events=[event_to_schema(e) for e in result.new_events],
        new_intel_reports=build_intel_schemas(db, result.new_intel),
        events=[event_to_schema(e) for e in service.list_events()],
        intel_reports=build_intel_schemas(db, service.list_intel()),
        assets=[asset_to_schema(a) for a in ops.list_assets()],
        operations=[operation_to_schema(o) for o in ops.list_operations()],
        resolved_operations=[operation_to_schema(o) for o in result.resolved_operations],
    )
    await broadcast_world_update("world.updated", response.model_dump(mode="json"))
    return response


@router.post("/advance", response_model=AdvanceResultSchema)
async def advance_time(payload: AdvanceTimeSchema, db: DbSession) -> AdvanceResultSchema:
    service = WorldSimulationService(db)
    result = service.advance_minutes(payload.minutes)
    ops = OperationsService(db)
    response = AdvanceResultSchema(
        clock=clock_to_schema(result.world),
        ticks_run=result.ticks_run,
        new_events=[event_to_schema(e) for e in result.new_events],
        new_intel_reports=build_intel_schemas(db, result.new_intel),
        events=[event_to_schema(e) for e in service.list_events()],
        intel_reports=build_intel_schemas(db, service.list_intel()),
        assets=[asset_to_schema(a) for a in ops.list_assets()],
        operations=[operation_to_schema(o) for o in ops.list_operations()],
        resolved_operations=[operation_to_schema(o) for o in result.resolved_operations],
    )
    await broadcast_world_update("world.updated", response.model_dump(mode="json"))
    return response
