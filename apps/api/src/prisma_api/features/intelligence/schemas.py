from __future__ import annotations

from pydantic import BaseModel, Field

from prisma_api.features.analysts.schemas import AnalystAssessmentSchema
from prisma_api.schemas.common import CoordinatesSchema


class IntelReportSchema(BaseModel):
    """Player-visible intelligence — never includes ground-truth or accuracy metadata."""

    id: str
    title: str
    description: str
    source: str = Field(description="SATINT | SIGINT | HUMINT | CYBER")
    confidence: int = Field(ge=0, le=100)
    timestamp: int = Field(description="Game time in minutes from crisis start")
    region: str
    coordinates: CoordinatesSchema
    analyst_assessments: list[AnalystAssessmentSchema] = []
    player_action: str | None = Field(
        default=None,
        description="Last action player took: ignore|request_more_intel|launch_recon|launch_strike",
    )

