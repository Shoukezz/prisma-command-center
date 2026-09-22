from sqlalchemy.orm import Session


class GameSessionRepository:
    """Persistence for player game instances."""

    def __init__(self, db: Session) -> None:
        self._db = db
