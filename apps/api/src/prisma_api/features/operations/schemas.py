from __future__ import annotations

from pydantic import BaseModel, Field


class AssetSchema(BaseModel):
    id: str
    name: str
    asset_type: str
    status: str
    supports_recon: bool
    supports_strike: bool


class OperationResultSchema(BaseModel):
    success: bool
    outcome_summary: str
    confidence_at_planning: int
    completed_at: int


class OperationSchema(BaseModel):
    id: str
    operation_type: str
    status: str
    region_name: str
    intel_confidence: int
    started_at: int
    completes_at: int
    duration_minutes: int
    asset_id: str
    asset_name: str
    intel_report_id: str
    result: OperationResultSchema | None = None


class PlanOperationSchema(BaseModel):
    operation_type: str = Field(description="recon | strike")
    intel_report_id: str
    asset_id: str
