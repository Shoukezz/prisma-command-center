"""Default PRISMA analyst roster."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from prisma_api.models import Analyst
from prisma_api.models.world import World

DEFAULT_ANALYSTS: list[tuple[str, str, float, str]] = [
    ("Dr. Elena Vasquez", "satellite_imagery", 0.78, "skeptical"),
    ("Marcus Cole", "signals_intelligence", 0.65, "hawkish"),
    ("Lin Wei", "cyber_threats", 0.72, "cyber_focus"),
    ("Sarah Okonkwo", "human_source", 0.55, "diplomatic"),
    ("Col. James Reed", "kinetic_operations", 0.70, "hawkish"),
    ("Anna Bergström", "regional_affairs", 0.68, "tech_optimist"),
]


def seed_analysts(db: Session, world: World) -> list[Analyst]:
    existing = db.query(Analyst).filter(Analyst.world_id == world.id).count()
    if existing > 0:
        return db.query(Analyst).filter(Analyst.world_id == world.id).all()

    analysts: list[Analyst] = []
    for name, specialty, reliability, bias in DEFAULT_ANALYSTS:
        analyst = Analyst(
            id=str(uuid.uuid4()),
            world_id=world.id,
            name=name,
            specialty=specialty,
            reliability=reliability,
            bias=bias,
        )
        db.add(analyst)
        analysts.append(analyst)
    db.commit()
    return analysts
