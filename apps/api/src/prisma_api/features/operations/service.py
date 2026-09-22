"""Operations planning, queueing, and time-based resolution."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from prisma_api.features.operations.constants import DURATION_MINUTES, OPERATION_TYPES
from prisma_api.features.operations.resolver import resolve_operation
from prisma_api.features.operations.seed_assets import seed_assets
from prisma_api.features.world.seed import ensure_world
from prisma_api.models import (
    ASSET_AVAILABLE,
    ASSET_IN_USE,
    OP_STATUS_ACTIVE,
    OP_STATUS_FAILED,
    OPERATION_RECON,
    OPERATION_STRIKE,
    Asset,
    IntelligenceReport,
    Operation,
)


class OperationsService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def _world(self):
        world = ensure_world(self._db)
        seed_assets(self._db, world)
        return world

    def list_assets(self) -> list[Asset]:
        world = self._world()
        return (
            self._db.query(Asset)
            .filter(Asset.world_id == world.id)
            .order_by(Asset.name)
            .all()
        )

    def list_operations(self, limit: int = 50) -> list[Operation]:
        world = self._world()
        return (
            self._db.query(Operation)
            .options(
                joinedload(Operation.asset),
                joinedload(Operation.result),
            )
            .filter(Operation.world_id == world.id)
            .order_by(Operation.started_at.desc())
            .limit(limit)
            .all()
        )

    def plan_operation(
        self,
        operation_type: str,
        intel_report_id: str,
        asset_id: str,
    ) -> Operation:
        if operation_type not in OPERATION_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Некоректний тип операції. Використайте: {', '.join(OPERATION_TYPES)}",
            )

        world = self._world()
        intel = (
            self._db.query(IntelligenceReport)
            .filter(
                IntelligenceReport.id == intel_report_id,
                IntelligenceReport.world_id == world.id,
            )
            .first()
        )
        if intel is None:
            raise HTTPException(status_code=404, detail="Розвідувальний звіт не знайдено")

        asset = (
            self._db.query(Asset)
            .filter(Asset.id == asset_id, Asset.world_id == world.id)
            .first()
        )
        if asset is None:
            raise HTTPException(status_code=404, detail="Ресурс не знайдено")
        if asset.status != ASSET_AVAILABLE:
            raise HTTPException(status_code=409, detail="Ресурс недоступний")

        if operation_type == OPERATION_RECON and not asset.supports_recon:
            raise HTTPException(status_code=400, detail="Ресурс не може виконувати розвідувальні операції")
        if operation_type == OPERATION_STRIKE and not asset.supports_strike:
            raise HTTPException(status_code=400, detail="Ресурс не може виконувати ударні операції")

        duration = DURATION_MINUTES[operation_type]
        started = world.game_minutes
        completes = started + duration

        operation = Operation(
            id=str(uuid.uuid4()),
            world_id=world.id,
            operation_type=operation_type,
            status=OP_STATUS_ACTIVE,
            intel_report_id=intel.id,
            asset_id=asset.id,
            region_name=intel.region_name,
            target_latitude=intel.latitude,
            target_longitude=intel.longitude,
            intel_confidence=intel.confidence,
            started_at=started,
            completes_at=completes,
            duration_minutes=duration,
        )
        asset.status = ASSET_IN_USE
        self._db.add(operation)
        self._db.commit()
        self._db.refresh(operation)
        return (
            self._db.query(Operation)
            .options(joinedload(Operation.asset), joinedload(Operation.result))
            .filter(Operation.id == operation.id)
            .one()
        )

    def resolve_due_operations(self, world_id: int, current_game_minutes: int) -> list[Operation]:
        """Complete operations whose time has elapsed."""
        due = (
            self._db.query(Operation)
            .options(joinedload(Operation.asset), joinedload(Operation.result))
            .filter(
                Operation.world_id == world_id,
                Operation.status == OP_STATUS_ACTIVE,
                Operation.completes_at <= current_game_minutes,
            )
            .all()
        )
        resolved: list[Operation] = []
        for operation in due:
            intel = (
                self._db.query(IntelligenceReport)
                .filter(IntelligenceReport.id == operation.intel_report_id)
                .first()
            )
            if intel is None:
                operation.status = OP_STATUS_FAILED
                operation.asset.status = ASSET_AVAILABLE
                resolved.append(operation)
                continue
            resolve_operation(self._db, operation, intel)
            resolved.append(operation)
        if resolved:
            self._db.commit()
        return resolved
