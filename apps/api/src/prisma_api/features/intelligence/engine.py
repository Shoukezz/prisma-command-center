"""Generate intelligence reports from world events — never expose ground truth."""

from __future__ import annotations

import random
import uuid
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from prisma_api.features.analysts.service import AnalystService
from prisma_api.features.intelligence.constants import (
    INTEL_SOURCES,
    MAX_REPORTS_PER_EVENT,
    MIN_REPORTS_PER_EVENT,
    PHANTOM_REPORT_CHANCE,
    SOURCE_PROFILES,
)
from prisma_api.features.intelligence.distortion import (
    distort_event_for_source,
    generate_phantom_content,
)
from prisma_api.models import Event, IntelligenceReport, Region, World


class IntelligenceEngine:
    """Produces player-visible intelligence from ground-truth simulation data."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def _all_regions(self) -> list[Region]:
        return self._db.query(Region).options(joinedload(Region.country)).all()

    def _pick_sources_for_event(self, event: Event) -> list[str]:
        count = random.randint(MIN_REPORTS_PER_EVENT, MAX_REPORTS_PER_EVENT)
        preferred = [
            code
            for code, profile in SOURCE_PROFILES.items()
            if event.event_type in profile.preferred_event_types
        ]
        pool = preferred if preferred and random.random() < 0.65 else list(INTEL_SOURCES)
        return random.sample(pool, k=min(count, len(pool)))

    def generate_for_event(self, world: World, event: Event) -> list[IntelligenceReport]:
        """Create one or more imperfect reports derived from a ground-truth event."""
        regions = self._all_regions()
        reports: list[IntelligenceReport] = []

        collection_delay = random.randint(0, 12)

        for source_code in self._pick_sources_for_event(event):
            profile = SOURCE_PROFILES[source_code]
            distorted = distort_event_for_source(event, profile, regions)
            report = IntelligenceReport(
                id=str(uuid.uuid4()),
                world_id=world.id,
                game_minutes=world.game_minutes + collection_delay,
                source=source_code,
                confidence=distorted.confidence,
                title=distorted.title,
                summary=distorted.description,
                region_name=distorted.region_name,
                latitude=distorted.latitude,
                longitude=distorted.longitude,
                related_event_id=event.id,
                content_accuracy=distorted.content_accuracy,
                location_accuracy=distorted.location_accuracy,
            )
            self._db.add(report)
            reports.append(report)

        return reports

    def generate_phantom(self, world: World) -> Optional[IntelligenceReport]:
        """Occasional false-positive report with no underlying event."""
        if random.random() > PHANTOM_REPORT_CHANCE:
            return None

        region = (
            self._db.query(Region)
            .options(joinedload(Region.country))
            .order_by(func.random())
            .first()
        )
        if region is None:
            return None

        source_code = random.choice(list(INTEL_SOURCES))
        profile = SOURCE_PROFILES[source_code]
        distorted = generate_phantom_content(region, profile, self._all_regions())

        report = IntelligenceReport(
            id=str(uuid.uuid4()),
            world_id=world.id,
            game_minutes=world.game_minutes + random.randint(5, 30),
            source=source_code,
            confidence=distorted.confidence,
            title=distorted.title,
            summary=distorted.description,
            region_name=distorted.region_name,
            latitude=distorted.latitude,
            longitude=distorted.longitude,
            related_event_id=None,
            content_accuracy=distorted.content_accuracy,
            location_accuracy=distorted.location_accuracy,
        )
        self._db.add(report)
        return report

    def generate_for_tick(self, world: World, events: list[Event]) -> list[IntelligenceReport]:
        reports: list[IntelligenceReport] = []
        for event in events:
            reports.extend(self.generate_for_event(world, event))
        phantom = self.generate_phantom(world)
        if phantom is not None:
            reports.append(phantom)
        if reports:
            self._db.flush()
            AnalystService(self._db).ensure_assessments(reports)
        return reports
