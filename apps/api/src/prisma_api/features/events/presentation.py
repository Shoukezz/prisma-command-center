"""Player-facing operational bulletins — degraded view of ground-truth events."""

from __future__ import annotations

import random

from prisma_api.features.world.schemas import EventSchema
from prisma_api.models import Event
from prisma_api.schemas.common import CoordinatesSchema

# Events reach the ops floor as flash traffic; wording is cautious and coordinates fuzzy.


def event_to_player_schema(event: Event) -> EventSchema:
    jitter = 0.25
    lat = event.latitude + random.uniform(-jitter, jitter)
    lng = event.longitude + random.uniform(-jitter, jitter)

    title = event.title
    if random.random() < 0.35:
        title = f"ТЕРМІНОВО: {title}"
    if random.random() < 0.25:
        title = title.replace("—", "— НЕПІДТВЕРДЖЕНО —", 1)

    summary = event.summary
    if random.random() < 0.4:
        summary = f"{summary} Оцінювання триває; деталі можуть змінитися."

    return EventSchema(
        id=event.id,
        game_minutes=event.game_minutes,
        title=title[:256],
        summary=summary,
        severity=event.severity if random.random() < 0.85 else "medium",
        event_type="situation_update",
        region=event.region_name,
        country=event.country_name if random.random() < 0.7 else "невідомо",
        coordinates=CoordinatesSchema(lat=lat, lng=lng),
    )
