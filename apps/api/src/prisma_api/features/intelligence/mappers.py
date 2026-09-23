from __future__ import annotations

from prisma_api.features.analysts.schemas import AnalystAssessmentSchema
from prisma_api.features.intelligence.schemas import IntelReportSchema
from prisma_api.models import IntelligenceReport
from prisma_api.schemas.common import CoordinatesSchema


def intel_to_schema(
    report: IntelligenceReport,
    analyst_assessments: list[AnalystAssessmentSchema] | None = None,
    player_action: str | None = None,
) -> IntelReportSchema:
    return IntelReportSchema(
        id=report.id,
        title=report.title,
        description=report.summary,
        source=report.source,
        confidence=report.confidence,
        timestamp=report.game_minutes,
        region=report.region_name,
        coordinates=CoordinatesSchema(lat=report.latitude, lng=report.longitude),
        analyst_assessments=analyst_assessments or [],
        player_action=player_action,
    )
