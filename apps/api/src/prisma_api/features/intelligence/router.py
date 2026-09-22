from fastapi import APIRouter, HTTPException, Query, status

from prisma_api.api.websocket import broadcast_world_update
from prisma_api.core.deps import DbSession
from prisma_api.features.intelligence.action_schemas import (
    IntelligenceActionSchema,
    TakeIntelligenceActionSchema,
)
from prisma_api.features.intelligence.action_service import IntelligenceActionService
from prisma_api.features.intelligence.enrichment import build_intel_schemas
from prisma_api.features.intelligence.schemas import IntelReportSchema
from prisma_api.features.intelligence.service import IntelligenceService
from prisma_api.features.world.seed import ensure_world

router = APIRouter()


@router.get("/reports", response_model=list[IntelReportSchema])
def list_intelligence_reports(
    db: DbSession,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[IntelReportSchema]:
    service = IntelligenceService(db)
    reports = service.list_reports(limit=limit)
    return build_intel_schemas(db, reports)


@router.post("/reports/{report_id}/action", response_model=IntelligenceActionSchema)
async def take_intelligence_action(
    report_id: str,
    payload: TakeIntelligenceActionSchema,
    db: DbSession,
) -> IntelligenceActionSchema:
    """Player takes action on an intelligence report.

    Actions:
    - ignore: Dismiss the report
    - request_more_intel: Request follow-up collection (generates new report)
    - launch_recon: Prepare recon operation (routes to operations/plan)
    - launch_strike: Prepare strike operation (routes to operations/plan)
    """
    world = ensure_world(db)
    service = IntelligenceActionService(db)

    action = service.take_action(
        world=world,
        intel_report_id=report_id,
        action_type=payload.action_type,
        reason=payload.reason,
    )
    db.commit()

    # Map related operation if one was created
    op_ref = None
    if action.related_operation:
        op_ref = {
            "id": action.related_operation.id,
            "operation_type": action.related_operation.operation_type,
            "status": action.related_operation.status,
            "started_at": action.related_operation.started_at,
            "completes_at": action.related_operation.completes_at,
        }

    response = IntelligenceActionSchema(
        id=action.id,
        intel_report_id=action.intel_report_id,
        action_type=action.action_type,
        status=action.status,
        taken_at=action.taken_at,
        reason=action.reason,
        related_operation=op_ref,
    )
    await broadcast_world_update(
        "intel.action",
        {"action_id": response.id, "report_id": response.intel_report_id},
    )
    return response


@router.get("/reports/{report_id}/actions", response_model=list[IntelligenceActionSchema])
def get_report_actions(report_id: str, db: DbSession) -> list[IntelligenceActionSchema]:
    """Get all actions player has taken on this report."""
    service = IntelligenceActionService(db)
    actions = service.get_actions_for_report(report_id)
    return [
        IntelligenceActionSchema(
            id=a.id,
            intel_report_id=a.intel_report_id,
            action_type=a.action_type,
            status=a.status,
            taken_at=a.taken_at,
            reason=a.reason,
            related_operation=(
                {
                    "id": a.related_operation.id,
                    "operation_type": a.related_operation.operation_type,
                    "status": a.related_operation.status,
                    "started_at": a.related_operation.started_at,
                    "completes_at": a.related_operation.completes_at,
                }
                if a.related_operation
                else None
            ),
        )
        for a in actions
    ]
