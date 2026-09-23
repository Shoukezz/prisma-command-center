"""Schemas for intelligence actions."""

from __future__ import annotations

from pydantic import BaseModel, Field


class OperationRefSchema(BaseModel):
    """Reference to a related operation."""

    id: str
    operation_type: str = Field(description="recon | strike")
    status: str = Field(description="active | completed | failed")
    started_at: int = Field(description="Game minutes when started")
    completes_at: int = Field(description="Game minutes when scheduled to complete")


class TakeIntelligenceActionSchema(BaseModel):
    """Request to take action on an intelligence report."""

    action_type: str = Field(
        description="ignore | request_more_intel | launch_recon | launch_strike"
    )
    reason: str | None = Field(default=None, description="Optional player reason")


class IntelligenceActionSchema(BaseModel):
    """Player action record."""

    id: str
    intel_report_id: str
    action_type: str
    status: str
    taken_at: int = Field(description="Game minutes when action taken")
    reason: str | None = None
    related_operation: OperationRefSchema | None = Field(
        default=None,
        description="If action launched an operation, reference to it",
    )
