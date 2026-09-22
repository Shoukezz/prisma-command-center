from sqlalchemy.orm import Session


class AuthRepository:
    """Persistence for users and sessions."""

    def __init__(self, db: Session) -> None:
        self._db = db
