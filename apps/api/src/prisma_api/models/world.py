from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from prisma_api.core.database import Base

if TYPE_CHECKING:
    from prisma_api.models.analyst import Analyst
    from prisma_api.models.event import Event, IntelligenceReport, WorldTick
    from prisma_api.models.geography import Country
    from prisma_api.models.intelligence_action import IntelligenceAction
    from prisma_api.models.operations import Asset, Operation


class World(Base):
    __tablename__ = "worlds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), default="PRISMA Crisis 2035")
    crisis_start_label: Mapped[str] = mapped_column(
        String(64), default="14 MAR 2035 0600Z"
    )
    game_minutes: Mapped[int] = mapped_column(Integer, default=0)
    is_paused: Mapped[bool] = mapped_column(Boolean, default=True)
    speed: Mapped[int] = mapped_column(Integer, default=1)
    ticks_elapsed: Mapped[int] = mapped_column(Integer, default=0)

    countries: Mapped[list[Country]] = relationship(back_populates="world")
    events: Mapped[list[Event]] = relationship(back_populates="world")
    ticks: Mapped[list[WorldTick]] = relationship(back_populates="world")
    intel_reports: Mapped[list[IntelligenceReport]] = relationship(back_populates="world")
    assets: Mapped[list[Asset]] = relationship(back_populates="world")
    operations: Mapped[list[Operation]] = relationship(back_populates="world")
    analysts: Mapped[list[Analyst]] = relationship(back_populates="world")
    intel_actions: Mapped[list[IntelligenceAction]] = relationship(back_populates="world")
