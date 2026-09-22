"""Intelligence collection source definitions."""

from __future__ import annotations

from dataclasses import dataclass

INTEL_SOURCES = ("SATINT", "SIGINT", "HUMINT", "CYBER")


@dataclass(frozen=True)
class SourceProfile:
    code: str
    location_error_deg: float
    detail_reliability: float
    preferred_event_types: tuple[str, ...]
    title_prefix: str


SOURCE_PROFILES = {
    "SATINT": SourceProfile(
        code="SATINT",
        location_error_deg=0.35,
        detail_reliability=0.72,
        preferred_event_types=("border_conflict", "economic_crisis"),
        title_prefix="IMINT/SATINT",
    ),
    "SIGINT": SourceProfile(
        code="SIGINT",
        location_error_deg=1.2,
        detail_reliability=0.58,
        preferred_event_types=("cyber_attack", "border_conflict"),
        title_prefix="SIGINT",
    ),
    "HUMINT": SourceProfile(
        code="HUMINT",
        location_error_deg=1.8,
        detail_reliability=0.45,
        preferred_event_types=("coup", "terrorist_incident"),
        title_prefix="HUMINT",
    ),
    "CYBER": SourceProfile(
        code="CYBER",
        location_error_deg=0.9,
        detail_reliability=0.65,
        preferred_event_types=("cyber_attack", "economic_crisis"),
        title_prefix="CYBER",
    ),
}

# How many collection attempts per ground-truth event per tick.
MIN_REPORTS_PER_EVENT = 1
MAX_REPORTS_PER_EVENT = 2

PHANTOM_REPORT_CHANCE = 0.18
