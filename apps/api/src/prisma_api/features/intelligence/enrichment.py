"""Attach analyst assessments to intelligence report API payloads."""

from __future__ import annotations

from sqlalchemy.orm import Session

from prisma_api.features.analysts.mappers import assessment_to_schema
from prisma_api.features.analysts.service import AnalystService
from prisma_api.features.intelligence.mappers import intel_to_schema
from prisma_api.features.intelligence.schemas import IntelReportSchema
from prisma_api.models import IntelligenceAction, IntelligenceReport


def build_intel_schemas(
    db: Session, reports: list[IntelligenceReport]
) -> list[IntelReportSchema]:
    if not reports:
        return []
    analyst_service = AnalystService(db)
    analyst_service.ensure_assessments(reports)
    grouped = analyst_service.assessments_for_reports([r.id for r in reports])

    # Get latest player action for each report
    report_actions: dict[str, IntelligenceAction | None] = {}
    for report in reports:
        latest_action = (
            db.query(IntelligenceAction)
            .filter(IntelligenceAction.intel_report_id == report.id)
            .order_by(IntelligenceAction.taken_at.desc())
            .first()
        )
        report_actions[report.id] = latest_action

    return [
        intel_to_schema(
            r,
            [assessment_to_schema(a) for a in grouped.get(r.id, [])],
            player_action=report_actions.get(r.id).action_type
            if report_actions.get(r.id)
            else None,
        )
        for r in reports
    ]
