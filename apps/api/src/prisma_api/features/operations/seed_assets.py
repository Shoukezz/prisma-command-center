"""Default strategic assets for a new world."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from prisma_api.models import ASSET_AVAILABLE, Asset
from prisma_api.models.world import World

DEFAULT_ASSETS: list[tuple[str, str, bool, bool]] = [
    ("Супутник SIGINT ORBIT-7", "satellite", True, True),
    ("Крило дронів Raven-12", "drone_wing", True, True),
    ("Польова група ECHO", "agent", True, False),
    ("Кіберпідрозділ MIRAGE", "cyber_team", False, True),
]


def seed_assets(db: Session, world: World) -> list[Asset]:
    existing = db.query(Asset).filter(Asset.world_id == world.id).count()
    if existing > 0:
        return db.query(Asset).filter(Asset.world_id == world.id).all()

    assets: list[Asset] = []
    for name, asset_type, recon, strike in DEFAULT_ASSETS:
        asset = Asset(
            id=str(uuid.uuid4()),
            world_id=world.id,
            name=name,
            asset_type=asset_type,
            status=ASSET_AVAILABLE,
            supports_recon=recon,
            supports_strike=strike,
        )
        db.add(asset)
        assets.append(asset)
    db.commit()
    return assets
