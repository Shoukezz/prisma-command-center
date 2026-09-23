from __future__ import annotations

from prisma_api.features.events.presentation import event_to_player_schema
from prisma_api.features.intelligence.schemas import IntelReportSchema
from prisma_api.features.operations.mappers import asset_to_schema, operation_to_schema
from prisma_api.features.world.constants import TICK_GAME_MINUTES
from prisma_api.features.world.schemas import (
    CitySchema,
    CountrySchema,
    EventSchema,
    GeographySchema,
    RegionSchema,
    WorldClockSchema,
    WorldStateSchema,
)
from prisma_api.models import City, Country, Event, Region, World
from prisma_api.schemas.common import CoordinatesSchema


def event_to_schema(event: Event) -> EventSchema:
    """Player-facing operational bulletin — not raw ground truth."""
    return event_to_player_schema(event)


def world_state_to_schema(
    world: World,
    events: list[Event],
    intel_reports: list[IntelReportSchema],
    assets: list | None = None,
    operations: list | None = None,
) -> WorldStateSchema:
    return WorldStateSchema(
        clock=clock_to_schema(world),
        events=[event_to_schema(e) for e in events],
        intel_reports=intel_reports,
        assets=[asset_to_schema(a) for a in (assets or [])],
        operations=[operation_to_schema(o) for o in (operations or [])],
    )


def clock_to_schema(world: World) -> WorldClockSchema:
    return WorldClockSchema(
        world_id=world.id,
        game_minutes=world.game_minutes,
        is_paused=world.is_paused,
        speed=world.speed,
        ticks_elapsed=world.ticks_elapsed,
        crisis_start_label=world.crisis_start_label,
        tick_game_minutes=TICK_GAME_MINUTES,
    )


def _city_schema(city: City) -> CitySchema:
    return CitySchema(
        id=city.id,
        name=city.name,
        coordinates=CoordinatesSchema(lat=city.latitude, lng=city.longitude),
    )


def _region_schema(region: Region) -> RegionSchema:
    return RegionSchema(
        id=region.id,
        name=region.name,
        coordinates=CoordinatesSchema(lat=region.latitude, lng=region.longitude),
        cities=[_city_schema(c) for c in region.cities],
    )


def _country_schema(country: Country) -> CountrySchema:
    return CountrySchema(
        id=country.id,
        code=country.code,
        name=country.name,
        bloc=country.bloc,
        regions=[_region_schema(r) for r in country.regions],
    )


def geography_to_schema(world: World) -> GeographySchema:
    return GeographySchema(
        world_id=world.id,
        countries=[_country_schema(c) for c in world.countries],
    )


# Re-export for routers that import from world.mappers
__all__ = [
    "event_to_schema",
    "clock_to_schema",
    "world_state_to_schema",
    "geography_to_schema",
    "EventSchema",
    "IntelReportSchema",
]
