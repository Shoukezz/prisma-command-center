from sqlalchemy.orm import Session

from prisma_api.features.world.constants import MAX_FEED_ITEMS
from prisma_api.features.world.seed import ensure_world
from prisma_api.models import IntelligenceReport


class IntelligenceService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_reports(self, limit: int = MAX_FEED_ITEMS) -> list[IntelligenceReport]:
        world = ensure_world(self._db)
        return (
            self._db.query(IntelligenceReport)
            .filter(IntelligenceReport.world_id == world.id)
            .order_by(IntelligenceReport.game_minutes.desc())
            .limit(limit)
            .all()
        )
