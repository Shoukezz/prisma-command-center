from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from prisma_api.core.database import Base

if TYPE_CHECKING:
    from prisma_api.models.world import World


class Analyst(Base):
    __tablename__ = "analysts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    world_id: Mapped[int] = mapped_column(ForeignKey("worlds.id"), index=True)
    name: Mapped[str] = mapped_column(String(128))
    specialty: Mapped[str] = mapped_column(String(64))
    reliability: Mapped[float] = mapped_column(Float)
    bias: Mapped[str] = mapped_column(String(64))

    world: Mapped[World] = relationship(back_populates="analysts")
    assessments: Mapped[list[AnalystAssessment]] = relationship(back_populates="analyst")


class AnalystAssessment(Base):
    __tablename__ = "analyst_assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    intel_report_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("intelligence_reports.id"), index=True
    )
    analyst_id: Mapped[str] = mapped_column(String(36), ForeignKey("analysts.id"), index=True)
    assessment: Mapped[str] = mapped_column(Text)
    assessed_confidence: Mapped[int] = mapped_column(Integer)
    game_minutes: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    analyst: Mapped[Analyst] = relationship(back_populates="assessments")
