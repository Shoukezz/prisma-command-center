from fastapi import APIRouter, Query

from prisma_api.api.websocket import broadcast_world_update
from prisma_api.core.deps import DbSession
from prisma_api.features.operations.mappers import asset_to_schema, operation_to_schema
from prisma_api.features.operations.schemas import (
    AssetSchema,
    OperationSchema,
    PlanOperationSchema,
)
from prisma_api.features.operations.service import OperationsService

router = APIRouter()


@router.get("/assets", response_model=list[AssetSchema])
def list_assets(db: DbSession) -> list[AssetSchema]:
    service = OperationsService(db)
    return [asset_to_schema(a) for a in service.list_assets()]


@router.get("", response_model=list[OperationSchema])
def list_operations(
    db: DbSession,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[OperationSchema]:
    service = OperationsService(db)
    return [operation_to_schema(o) for o in service.list_operations(limit=limit)]


@router.post("/plan", response_model=OperationSchema)
async def plan_operation(payload: PlanOperationSchema, db: DbSession) -> OperationSchema:
    service = OperationsService(db)
    operation = service.plan_operation(
        payload.operation_type,
        payload.intel_report_id,
        payload.asset_id,
    )
    response = operation_to_schema(operation)
    await broadcast_world_update("operation.planned", {"operation_id": response.id})
    return response
