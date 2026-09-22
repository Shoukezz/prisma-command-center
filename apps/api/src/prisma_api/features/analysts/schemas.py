from __future__ import annotations

from pydantic import BaseModel, Field


class AnalystSchema(BaseModel):
    id: str
    name: str
    specialty: str
    reliability: float = Field(ge=0, le=1)
    bias: str


class AnalystAssessmentSchema(BaseModel):
    id: str
    analyst_id: str
    analyst_name: str
    specialty: str
    bias: str
    reliability: float
    assessment: str
    assessed_confidence: int = Field(ge=0, le=100)
    timestamp: int
