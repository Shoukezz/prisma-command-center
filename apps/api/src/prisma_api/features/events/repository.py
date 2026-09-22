from sqlalchemy.orm import Session


class EventsRepository:
    """Persistence for world events."""

    def __init__(self, db: Session) -> None:
        self._db = db
