from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from prisma_api.core.database import Base

if TYPE_CHECKING:
    from prisma_api.models.intelligence_action import IntelligenceAction
    from prisma_api.models.world import World


class WorldTick(Base):
    __tablename__ = "world_ticks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    world_id: Mapped[int] = mapped_column(ForeignKey("worlds.id"), index=True)
    tick_number: Mapped[int] = mapped_column(Integer)
    game_minutes_at_tick: Mapped[int] = mapped_column(Integer)
    events_generated: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    world: Mapped[World] = relationship(back_populates="ticks")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    world_id: Mapped[int] = mapped_column(ForeignKey("worlds.id"), index=True)
    tick_number: Mapped[int] = mapped_column(Integer, index=True)
    game_minutes: Mapped[int] = mapped_column(Integer, index=True)
    event_type: Mapped[str] = mapped_column(String(64))
    severity: Mapped[str] = mapped_column(String(16))
    title: Mapped[str] = mapped_column(String(256))
    summary: Mapped[str] = mapped_column(Text)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("regions.id"), nullable=True)
    region_name: Mapped[str] = mapped_column(String(128))
    country_name: Mapped[str] = mapped_column(String(128), default="")
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    world: Mapped[World] = relationship(back_populates="events")


class IntelligenceReport(Base):
    __tablename__ = "intelligence_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    world_id: Mapped[int] = mapped_column(ForeignKey("worlds.id"), index=True)
    game_minutes: Mapped[int] = mapped_column(Integer, index=True)
    source: Mapped[str] = mapped_column(String(16))
    confidence: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(256))
    summary: Mapped[str] = mapped_column(Text)
    region_name: Mapped[str] = mapped_column(String(128))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    related_event_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    requested_by_action_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey(
            "intelligence_actions.id",
            name="fk_intelligence_reports_requested_by_action",
            use_alter=True,
        ),
        nullable=True,
    )
    content_accuracy: Mapped[float] = mapped_column(Float, default=0.5)
    location_accuracy: Mapped[float] = mapped_column(Float, default=0.5)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    world: Mapped[World] = relationship(back_populates="intel_reports")
    actions: Mapped[list[IntelligenceAction]] = relationship(
        back_populates="intel_report",
        foreign_keys="IntelligenceAction.intel_report_id",
    )
    requested_by_action: Mapped[IntelligenceAction | None] = relationship(
        back_populates="follow_up_intel",
        foreign_keys=[requested_by_action_id]
    )
