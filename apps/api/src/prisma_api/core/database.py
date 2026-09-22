from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from prisma_api.core.config import get_settings


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all models."""


def _create_engine():
    settings = get_settings()
    connect_args: dict[str, object] = {}
    if settings.database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(settings.database_url, connect_args=connect_args)


engine = _create_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create tables for registered models. Migrations preferred in production."""
    import prisma_api.models  # noqa: F401 — register models

    # Tests use a dedicated database and start from an empty schema. Never infer
    # this from the process name: importing pytest in a development server must
    # not erase a player's local campaign.
    if get_settings().environment == "test":
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
