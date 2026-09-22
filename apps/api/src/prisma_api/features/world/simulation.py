"""World clock and tick orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from prisma_api.features.analysts.seed import seed_analysts
from prisma_api.features.events.event_engine import process_tick
from prisma_api.features.operations.seed_assets import seed_assets
from prisma_api.features.operations.service import OperationsService
from prisma_api.features.world.constants import MAX_FEED_ITEMS, TICK_GAME_MINUTES
from prisma_api.features.world.seed import ensure_world
from prisma_api.models import (
    Country,
    Event,
    IntelligenceReport,
    Operation,
    Region,
    World,
    WorldTick,
)


@dataclass
class AdvanceResult:
    world: World
    ticks_run: int
    new_events: list[Event]
    new_intel: list[IntelligenceReport]
    resolved_operations: list[Operation]


class WorldSimulationService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_active_world(self) -> World:
        world = ensure_world(self._db)
        seed_assets(self._db, world)
        seed_analysts(self._db, world)
        return world

    def _resolve_operations(self, world: World) -> list[Operation]:
        return OperationsService(self._db).resolve_due_operations(
            world.id, world.game_minutes
        )

    def run_single_tick(self, world: Optional[World] = None) -> AdvanceResult:
        world = world or self.get_active_world()
        world.game_minutes += TICK_GAME_MINUTES
        world.ticks_elapsed += 1
        tick_number = world.ticks_elapsed

        tick_record = WorldTick(
            world_id=world.id,
            tick_number=tick_number,
            game_minutes_at_tick=world.game_minutes,
            events_generated=0,
        )
        self._db.add(tick_record)
        self._db.flush()

        generation = process_tick(self._db, world, tick_number)
        tick_record.events_generated = len(generation.events)
        resolved = self._resolve_operations(world)

        self._db.commit()
        self._db.refresh(world)

        return AdvanceResult(
            world=world,
            ticks_run=1,
            new_events=generation.events,
            new_intel=generation.intel_reports,
            resolved_operations=resolved,
        )

    def advance_minutes(self, minutes: int, world: Optional[World] = None) -> AdvanceResult:
        if minutes <= 0:
            world = world or self.get_active_world()
            return AdvanceResult(
                world=world,
                ticks_run=0,
                new_events=[],
                new_intel=[],
                resolved_operations=[],
            )

        world = world or self.get_active_world()
        full_ticks = minutes // TICK_GAME_MINUTES
        remainder = minutes % TICK_GAME_MINUTES

        all_events: list[Event] = []
        all_intel: list[IntelligenceReport] = []
        all_resolved: list[Operation] = []

        for _ in range(full_ticks):
            result = self.run_single_tick(world)
            all_events.extend(result.new_events)
            all_intel.extend(result.new_intel)
            all_resolved.extend(result.resolved_operations)

        if remainder > 0:
            world.game_minutes += remainder
            all_resolved.extend(self._resolve_operations(world))
            self._db.commit()
            self._db.refresh(world)

        return AdvanceResult(
            world=world,
            ticks_run=full_ticks,
            new_events=all_events,
            new_intel=all_intel,
            resolved_operations=all_resolved,
        )

    def update_clock(
        self,
        *,
        is_paused: Optional[bool] = None,
        speed: Optional[int] = None,
        world: Optional[World] = None,
    ) -> World:
        world = world or self.get_active_world()
        if is_paused is not None:
            world.is_paused = is_paused
        if speed is not None:
            world.speed = speed
        self._db.commit()
        self._db.refresh(world)
        return world

    def list_events(self, limit: int = MAX_FEED_ITEMS) -> list[Event]:
        world = self.get_active_world()
        return (
            self._db.query(Event)
            .filter(Event.world_id == world.id)
            .order_by(Event.game_minutes.desc(), Event.created_at.desc())
            .limit(limit)
            .all()
        )

    def list_intel(self, limit: int = MAX_FEED_ITEMS) -> list[IntelligenceReport]:
        world = self.get_active_world()
        return (
            self._db.query(IntelligenceReport)
            .filter(IntelligenceReport.world_id == world.id)
            .order_by(IntelligenceReport.game_minutes.desc())
            .limit(limit)
            .all()
        )

    def get_world_with_geography(self) -> World:
        world = self.get_active_world()
        loaded = (
            self._db.query(World)
            .options(
                joinedload(World.countries)
                .joinedload(Country.regions)
                .joinedload(Region.cities)
            )
            .filter(World.id == world.id)
            .first()
        )
        return loaded or world
