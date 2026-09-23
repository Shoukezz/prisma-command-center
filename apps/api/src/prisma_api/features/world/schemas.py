from __future__ import annotations

from pydantic import BaseModel, Field

from prisma_api.features.intelligence.schemas import IntelReportSchema
from prisma_api.features.operations.schemas import AssetSchema, OperationSchema
from prisma_api.schemas.common import CoordinatesSchema


class CitySchema(BaseModel):
    id: int
    name: str
    coordinates: CoordinatesSchema


class RegionSchema(BaseModel):
    id: int
    name: str
    coordinates: CoordinatesSchema
    cities: list[CitySchema]


class CountrySchema(BaseModel):
    id: int
    code: str
    name: str
    bloc: str
    regions: list[RegionSchema]


class WorldClockSchema(BaseModel):
    world_id: int
    game_minutes: int
    is_paused: bool
    speed: int
    ticks_elapsed: int
    crisis_start_label: str
    tick_game_minutes: int = Field(description="Game minutes advanced per tick")


class EventSchema(BaseModel):
    id: str
    game_minutes: int
    title: str
    summary: str
    severity: str
    event_type: str
    region: str
    country: str
    coordinates: CoordinatesSchema


class WorldStateSchema(BaseModel):
    clock: WorldClockSchema
    events: list[EventSchema]
    intel_reports: list[IntelReportSchema]
    assets: list[AssetSchema] = []
    operations: list[OperationSchema] = []


class GeographySchema(BaseModel):
    world_id: int
    countries: list[CountrySchema]


class ClockUpdateSchema(BaseModel):
    is_paused: bool | None = None
    speed: int | None = Field(default=None, ge=1, le=4)


class AdvanceTimeSchema(BaseModel):
    minutes: int = Field(ge=1, le=24 * 60)


class AdvanceResultSchema(BaseModel):
    clock: WorldClockSchema
    ticks_run: int
    new_events: list[EventSchema]
    new_intel_reports: list[IntelReportSchema]
    events: list[EventSchema]
    intel_reports: list[IntelReportSchema]
    assets: list[AssetSchema] = []
    operations: list[OperationSchema] = []
    resolved_operations: list[OperationSchema] = []
