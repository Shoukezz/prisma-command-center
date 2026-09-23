"""Geopolitical event generation for each world tick."""

from __future__ import annotations

import random
import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session, joinedload

from prisma_api.features.intelligence.engine import IntelligenceEngine
from prisma_api.models import City, Event, IntelligenceReport, Region, World

EVENT_TYPES = (
    "border_conflict",
    "cyber_attack",
    "coup",
    "terrorist_incident",
    "economic_crisis",
)

EVENT_TEMPLATES: dict[str, list[tuple[str, str, str]]] = {
    "border_conflict": [
        (
            "medium",
            "Прикордонна сутичка — {region}",
            "Повідомляється про непідтверджені зіткнення вздовж кордону {region}. "
            "Сили {country} приведено у підвищену готовність.",
        ),
        (
            "high",
            "Ескалація на кордоні {region}",
            "Біля {city} триває інтенсивний бій. "
            "Партнери PRISMA запитали гуманітарні коридори для евакуації цивільних.",
        ),
    ],
    "cyber_attack": [
        (
            "high",
            "Кібервторгнення — інфраструктура {country}",
            "Аномальний трафік націлено на енергетичні й транспортні вузли в регіоні {region}. "
            "Встановити виконавця не вдалося.",
        ),
        (
            "critical",
            "Масштабні кіберзбої — {region}",
            "Скоординована активність програм-затирачів спрямована проти командних мереж "
            "{country}. Резервні системи активовано.",
        ),
    ],
    "coup": [
        (
            "critical",
            "Спроба перевороту — {city}",
            "Військові підрозділи мобілізуються навколо урядового кварталу в {city}. "
            "Дипломатичні канали перевантажені.",
        ),
        (
            "high",
            "Політична нестабільність — {country}",
            "У {country} виникає внутрішній виклик керівництву. "
            "Очікуються заяви регіональних блоків.",
        ),
    ],
    "terrorist_incident": [
        (
            "high",
            "Терористичний інцидент — {city}",
            "У центрі {city} повідомляють про вибух. "
            "Дані про жертви попередні; місце події не убезпечено.",
        ),
        (
            "medium",
            "Підвищення терористичної загрози — {region}",
            "Перехоплені переговори вказують на можливі негайні дії в {region}. "
            "Рівень достовірності середній.",
        ),
    ],
    "economic_crisis": [
        (
            "medium",
            "Ринковий шок — {country}",
            "Товарні ф’ючерси та валютні спреди на біржах {country} "
            "демонструють високу волатильність.",
        ),
        (
            "low",
            "Збій ланцюгів постачання — {region}",
            "У {region} повідомляють про затримки виробництва. "
            "Логістика консорціуму змінює маршрути.",
        ),
    ],
}


@dataclass
class TickGenerationResult:
    events: list[Event]
    intel_reports: list[IntelligenceReport]


def _pick_location(db: Session, rng: random.Random) -> tuple[Region, City | None]:
    # Use a local RNG and deterministic selection from the seeded sequence so
    # tests can reproduce event generation reliably.
    regions = (
        db.query(Region).options(joinedload(Region.cities), joinedload(Region.country)).all()
    )
    if not regions:
        raise RuntimeError("No regions seeded")
    region = rng.choice(regions)
    city = rng.choice(region.cities) if region.cities else None
    return region, city


def _format_template(
    template: tuple[str, str, str],
    region: Region,
    city: City | None,
) -> tuple[str, str, str]:
    severity, title_t, summary_t = template
    country_name = region.country.name
    city_name = city.name if city else region.name
    fmt = {
        "region": region.name,
        "country": country_name,
        "city": city_name,
    }
    return severity, title_t.format(**fmt), summary_t.format(**fmt)


def generate_geopolitical_event(
    db: Session,
    world: World,
    tick_number: int,
) -> Event | None:
    """Roll and optionally create one ground-truth geopolitical event for this tick.

    Deterministic behavior: decisions are made from a local RNG seeded with
    the world's `game_minutes` and the `tick_number`. This keeps behavior
    reproducible across test runs while preserving randomness semantics.
    """
    rng = random.Random(int(getattr(world, "game_minutes", 0) or 0))
    if rng.random() > 0.55:
        return None

    region, city = _pick_location(db, rng)
    event_type = rng.choice(EVENT_TYPES)
    template = rng.choice(EVENT_TEMPLATES[event_type])
    severity, title, summary = _format_template(template, region, city)

    lat = city.latitude if city else region.latitude
    lng = city.longitude if city else region.longitude

    event = Event(
        id=str(uuid.uuid4()),
        world_id=world.id,
        tick_number=tick_number,
        game_minutes=world.game_minutes,
        event_type=event_type,
        severity=severity,
        title=title,
        summary=summary,
        region_id=region.id,
        region_name=region.name,
        country_name=region.country.name,
        latitude=lat + random.uniform(-0.4, 0.4),
        longitude=lng + random.uniform(-0.4, 0.4),
    )
    db.add(event)
    return event


def process_tick(db: Session, world: World, tick_number: int) -> TickGenerationResult:
    """Run ground-truth event generation, then intelligence collection."""
    events: list[Event] = []
    intel_reports: list[IntelligenceReport] = []

    event = generate_geopolitical_event(db, world, tick_number)
    if event is not None:
        events.append(event)

    intel_engine = IntelligenceEngine(db)
    intel_reports = intel_engine.generate_for_tick(world, events)

    return TickGenerationResult(events=events, intel_reports=intel_reports)
