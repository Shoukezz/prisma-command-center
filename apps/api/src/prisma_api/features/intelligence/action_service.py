"""Service for handling player decisions on intelligence reports."""

from __future__ import annotations

import random
import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from prisma_api.models import (
    ACTION_IGNORE,
    ACTION_LAUNCH_RECON,
    ACTION_LAUNCH_STRIKE,
    ACTION_REQUEST_MORE,
    ACTION_STATUS_COMPLETED,
    ACTION_TYPES,
    ASSET_AVAILABLE,
    OP_STATUS_ACTIVE,
    OPERATION_RECON,
    OPERATION_STRIKE,
    Asset,
    IntelligenceAction,
    IntelligenceReport,
    Operation,
)
from prisma_api.models.world import World


class IntelligenceActionService:
    """Processes player actions on intelligence reports."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def take_action(
        self,
        world: World,
        intel_report_id: str,
        action_type: str,
        reason: str | None = None,
    ) -> IntelligenceAction:
        """Player takes action on an intelligence report.

        Actions:
        - ignore: Player dismisses the report; no consequence
        - request_more_intel: Request follow-up intelligence on same target
        - launch_recon: Plan recon operation on report target
        - launch_strike: Plan strike operation on report target

        Args:
            world: Active world
            intel_report_id: Report ID player is acting on
            action_type: One of ACTION_TYPES
            reason: Optional text reason from player

        Returns:
            IntelligenceAction record

        Raises:
            HTTPException if report not found or action invalid
        """
        if action_type not in ACTION_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Некоректна дія. Використайте: {', '.join(ACTION_TYPES)}",
            )

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

        action = IntelligenceAction(
            id=str(uuid.uuid4()),
            world_id=world.id,
            intel_report_id=intel_report_id,
            action_type=action_type,
            taken_at=world.game_minutes,
            reason=reason,
        )
        self._db.add(action)

        # Process action
        if action_type == ACTION_IGNORE:
            # No effect; just record player dismissed it
            action.status = ACTION_STATUS_COMPLETED

        elif action_type == ACTION_REQUEST_MORE:
            # Generate a follow-up report on the same target
            # Delay: 15-30 game minutes
            # Accuracy: slightly better than original
            follow_up = self._generate_follow_up_intel(world, intel, action)
            self._db.add(follow_up)
            action.status = ACTION_STATUS_COMPLETED

        elif action_type == ACTION_LAUNCH_RECON:
            # Auto-plan recon operation on the target
            operation = self._plan_auto_operation(world, intel, action, OPERATION_RECON)
            if operation:
                action.related_operation = operation
                action.status = ACTION_STATUS_COMPLETED

        elif action_type == ACTION_LAUNCH_STRIKE:
            # Auto-plan strike operation on the target
            operation = self._plan_auto_operation(world, intel, action, OPERATION_STRIKE)
            if operation:
                action.related_operation = operation
                action.status = ACTION_STATUS_COMPLETED

        self._db.flush()
        return action

    def _generate_follow_up_intel(
        self,
        world: World,
        original_intel: IntelligenceReport,
        action: IntelligenceAction,
    ) -> IntelligenceReport:
        """Generate follow-up intelligence from request_more_intel action."""
        delay = random.randint(15, 30)
        follow_up = IntelligenceReport(
            id=str(uuid.uuid4()),
            world_id=world.id,
            game_minutes=world.game_minutes + delay,
            source=original_intel.source,
            # Confidence higher (player requested more focus)
            confidence=min(95, original_intel.confidence + random.randint(5, 15)),
            title=f"{original_intel.title} [Додатковий збір даних]",
            summary=f"Додатковий збір даних щодо {original_intel.region_name}: "
            + self._generate_follow_up_details(original_intel),
            region_name=original_intel.region_name,
            # Slight refinement of coordinates
            latitude=original_intel.latitude
            + random.uniform(-0.1, 0.1),
            longitude=original_intel.longitude
            + random.uniform(-0.1, 0.1),
            related_event_id=original_intel.related_event_id,
            # Better accuracy (more focused collection)
            content_accuracy=min(
                1.0, original_intel.content_accuracy + random.uniform(0.05, 0.15)
            ),
            location_accuracy=min(
                1.0, original_intel.location_accuracy + random.uniform(0.05, 0.15)
            ),
        )
        follow_up.requested_by_action_id = action.id
        return follow_up

    def _generate_follow_up_details(self, original: IntelligenceReport) -> str:
        """Generate text description of follow-up collection."""
        templates = [
            "Оновлений збір даних підтверджує продовження активності.",
            "Через вторинне джерело отримано уточнені дані про ціль.",
            "Зіставлення даних різних джерел підвищує достовірність.",
            "Аналіз прогалин у зборі даних завершено; активність триває.",
            "Розширення зони спостереження дало додаткові індикатори.",
        ]
        return random.choice(templates)

    def _plan_auto_operation(
        self,
        world: World,
        intel: IntelligenceReport,
        action: IntelligenceAction,
        operation_type: str,
    ) -> Operation | None:
        """Automatically plan a recon or strike operation on the intelligence target.

        Returns None if no suitable asset is available.
        """
        # Find available asset capable of this operation
        query = self._db.query(Asset).filter(
            Asset.world_id == world.id,
            Asset.status == ASSET_AVAILABLE,
        )

        if operation_type == OPERATION_RECON:
            query = query.filter(Asset.supports_recon.is_(True))
        elif operation_type == OPERATION_STRIKE:
            query = query.filter(Asset.supports_strike.is_(True))

        asset = query.first()
        if not asset:
            return None

        # Duration constants
        duration_map = {OPERATION_RECON: 45, OPERATION_STRIKE: 90}
        duration = duration_map.get(operation_type, 45)
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
            triggering_action_id=action.id,
        )
        asset.status = "in_use"
        self._db.add(operation)
        self._db.flush()
        self._db.refresh(operation)
        return operation

    def list_actions(self, world: World, limit: int = 50) -> list[IntelligenceAction]:
        """List all player actions on this world."""
        return (
            self._db.query(IntelligenceAction)
            .filter(IntelligenceAction.world_id == world.id)
            .order_by(IntelligenceAction.taken_at.desc())
            .limit(limit)
            .all()
        )

    def get_actions_for_report(
        self, intel_report_id: str
    ) -> list[IntelligenceAction]:
        """Get all actions player has taken on a specific report."""
        return (
            self._db.query(IntelligenceAction)
            .filter(IntelligenceAction.intel_report_id == intel_report_id)
            .order_by(IntelligenceAction.taken_at.desc())
            .all()
        )
