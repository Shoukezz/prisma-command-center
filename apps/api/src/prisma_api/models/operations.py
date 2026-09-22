from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from prisma_api.core.database import Base

OPERATION_RECON = "recon"
OPERATION_STRIKE = "strike"

OP_STATUS_PLANNED = "planned"
OP_STATUS_ACTIVE = "active"
OP_STATUS_COMPLETED = "completed"
OP_STATUS_FAILED = "failed"

ASSET_AVAILABLE = "available"
ASSET_IN_USE = "in_use"
ASSET_DAMAGED = "damaged"
ASSET_DESTROYED = "destroyed"


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    world_id: Mapped[int] = mapped_column(ForeignKey("worlds.id"), index=True)
    name: Mapped[str] = mapped_column(String(128))
    asset_type: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16), default=ASSET_AVAILABLE)
    supports_recon: Mapped[bool] = mapped_column(default=True)
    supports_strike: Mapped[bool] = mapped_column(default=False)

    world: Mapped[World] = relationship(back_populates="assets")
    operations: Mapped[list[Operation]] = relationship(back_populates="asset")


class Operation(Base):
    __tablename__ = "operations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    world_id: Mapped[int] = mapped_column(ForeignKey("worlds.id"), index=True)
    operation_type: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(16), default=OP_STATUS_ACTIVE)
    intel_report_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("intelligence_reports.id")
    )
    asset_id: Mapped[str] = mapped_column(String(36), ForeignKey("assets.id"))
    region_name: Mapped[str] = mapped_column(String(128))
    target_latitude: Mapped[float] = mapped_column(Float)
    target_longitude: Mapped[float] = mapped_column(Float)
    intel_confidence: Mapped[int] = mapped_column(Integer)
    started_at: Mapped[int] = mapped_column(Integer)
    completes_at: Mapped[int] = mapped_column(Integer, index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer)
    triggering_action_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("intelligence_actions.id"), nullable=True
    )

    world: Mapped[World] = relationship(back_populates="operations")
    asset: Mapped[Asset] = relationship(back_populates="operations")
    result: Mapped[Optional["OperationResult"]] = relationship(
        back_populates="operation", uselist=False
    )
    triggering_action: Mapped[Optional["IntelligenceAction"]] = relationship(
        back_populates="related_operation",
        foreign_keys=[triggering_action_id],
    )


class OperationResult(Base):
    __tablename__ = "operation_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    operation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("operations.id"), unique=True
    )
    success: Mapped[bool] = mapped_column()
    outcome_summary: Mapped[str] = mapped_column(Text)
    confidence_at_planning: Mapped[int] = mapped_column(Integer)
    completed_at: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    operation: Mapped[Operation] = relationship(back_populates="result")
