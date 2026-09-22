from sqlalchemy.orm import Session


class WorldRepository:
    """Persistence for world, countries, regions, cities."""

    def __init__(self, db: Session) -> None:
        self._db = db
