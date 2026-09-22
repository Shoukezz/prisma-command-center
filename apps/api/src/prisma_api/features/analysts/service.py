from __future__ import annotations

import random
import uuid
from collections import defaultdict
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from prisma_api.features.analysts.constants import (
    ASSESSMENTS_PER_REPORT_MAX,
    ASSESSMENTS_PER_REPORT_MIN,
    SOURCE_SPECIALTY_AFFINITY,
)
from prisma_api.features.analysts.interpretation import interpret_report
from prisma_api.features.analysts.seed import seed_analysts
from prisma_api.features.world.seed import ensure_world
from prisma_api.models import Analyst, AnalystAssessment, IntelligenceReport


class AnalystService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def _world(self):
        world = ensure_world(self._db)
        seed_analysts(self._db, world)
        return world

    def list_analysts(self) -> list[Analyst]:
        world = self._world()
        return (
            self._db.query(Analyst)
            .filter(Analyst.world_id == world.id)
            .order_by(Analyst.name)
            .all()
        )

    def _pick_analysts_for_report(
        self, report: IntelligenceReport, roster: list[Analyst]
    ) -> list[Analyst]:
        count = random.randint(ASSESSMENTS_PER_REPORT_MIN, ASSESSMENTS_PER_REPORT_MAX)
        affinity = SOURCE_SPECIALTY_AFFINITY.get(report.source)
        preferred = [a for a in roster if a.specialty == affinity]
        others = [a for a in roster if a.specialty != affinity]
        random.shuffle(preferred)
        random.shuffle(others)
        ordered = preferred + others
        return ordered[: min(count, len(ordered))]

    def create_assessments_for_report(
        self, report: IntelligenceReport, roster: Optional[list[Analyst]] = None
    ) -> list[AnalystAssessment]:
        world = self._world()
        roster = roster or self.list_analysts()
        if not roster:
            return []

        existing = (
            self._db.query(AnalystAssessment)
            .filter(AnalystAssessment.intel_report_id == report.id)
            .count()
        )
        if existing > 0:
            return (
                self._db.query(AnalystAssessment)
                .options(joinedload(AnalystAssessment.analyst))
                .filter(AnalystAssessment.intel_report_id == report.id)
                .all()
            )

        selected = self._pick_analysts_for_report(report, roster)
        assessments: list[AnalystAssessment] = []
        delay = random.randint(2, 18)

        for analyst in selected:
            result = interpret_report(report, analyst)
            row = AnalystAssessment(
                id=str(uuid.uuid4()),
                intel_report_id=report.id,
                analyst_id=analyst.id,
                assessment=result.assessment,
                assessed_confidence=result.assessed_confidence,
                game_minutes=report.game_minutes + delay,
            )
            self._db.add(row)
            assessments.append(row)

        return assessments

    def ensure_assessments(self, reports: list[IntelligenceReport]) -> None:
        if not reports:
            return
        roster = self.list_analysts()
        for report in reports:
            self.create_assessments_for_report(report, roster)
        self._db.commit()

    def assessments_for_reports(
        self, report_ids: list[str]
    ) -> dict[str, list[AnalystAssessment]]:
        if not report_ids:
            return {}
        rows = (
            self._db.query(AnalystAssessment)
            .options(joinedload(AnalystAssessment.analyst))
            .filter(AnalystAssessment.intel_report_id.in_(report_ids))
            .all()
        )
        grouped: dict[str, list[AnalystAssessment]] = defaultdict(list)
        for row in rows:
            grouped[row.intel_report_id].append(row)
        return grouped
