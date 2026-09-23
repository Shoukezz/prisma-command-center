"""Player actions on intelligence reports."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from prisma_api.core.database import Base

if TYPE_CHECKING:
    from prisma_api.models.event import IntelligenceReport
    from prisma_api.models.operations import Operation
    from prisma_api.models.world import World

# Action types
ACTION_IGNORE = "ignore"
ACTION_REQUEST_MORE = "request_more_intel"
ACTION_LAUNCH_RECON = "launch_recon"
ACTION_LAUNCH_STRIKE = "launch_strike"

ACTION_TYPES = [ACTION_IGNORE, ACTION_REQUEST_MORE, ACTION_LAUNCH_RECON, ACTION_LAUNCH_STRIKE]

# Action status
ACTION_STATUS_PENDING = "pending"
ACTION_STATUS_COMPLETED = "completed"
ACTION_STATUS_FAILED = "failed"


class IntelligenceAction(Base):
    """Track player decisions on intelligence reports."""

    __tablename__ = "intelligence_actions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    world_id: Mapped[int] = mapped_column(ForeignKey("worlds.id"), index=True)
    intel_report_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("intelligence_reports.id"), index=True
    )
    action_type: Mapped[str] = mapped_column(String(24))
    status: Mapped[str] = mapped_column(String(16), default=ACTION_STATUS_PENDING)
    taken_at: Mapped[int] = mapped_column(Integer)  # game_minutes when action taken
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    world: Mapped[World] = relationship(back_populates="intel_actions")
    intel_report: Mapped[IntelligenceReport] = relationship(
        back_populates="actions",
        foreign_keys=[intel_report_id],
    )
    related_operation: Mapped[Operation | None] = relationship(
        back_populates="triggering_action",
        foreign_keys="Operation.triggering_action_id",
    )
    follow_up_intel: Mapped[list[IntelligenceReport]] = relationship(
        back_populates="requested_by_action",
        foreign_keys="IntelligenceReport.requested_by_action_id",
    )
