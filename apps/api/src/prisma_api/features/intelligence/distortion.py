"""Transform ground-truth events into imperfect intelligence assessments."""

from __future__ import annotations

import random
from dataclasses import dataclass

from prisma_api.features.intelligence.constants import SourceProfile
from prisma_api.models import Event, Region

EVENT_TYPE_PLAYER_LABELS = {
    "border_conflict": "прикордонна активність",
    "cyber_attack": "кіберінцидент",
    "coup": "нестабільність уряду",
    "terrorist_incident": "активність, пов’язана з тероризмом",
    "economic_crisis": "економічний збій",
}

SEVERITY_PLAYER_LABELS = {
    "low": "звичайний",
    "medium": "підвищений",
    "high": "серйозний",
    "critical": "критичний",
}

WRONG_TYPE_LABELS = [
    "логістична аномалія",
    "невстановлене переміщення військ",
    "громадські заворушення",
    "збій зв’язку",
    "промислова аварія",
]

WRONG_REGION_SUFFIXES = [
    "сектор",
    "коридор",
    "театр",
    "зона",
]


@dataclass
class DistortedReportContent:
    title: str
    description: str
    region_name: str
    latitude: float
    longitude: float
    confidence: int
    content_accuracy: float
    location_accuracy: float


def _mislabel_event_type(true_type: str, reliability: float) -> str:
    if random.random() < reliability:
        return EVENT_TYPE_PLAYER_LABELS.get(true_type, true_type.replace("_", " "))
    return random.choice(WRONG_TYPE_LABELS)


def _mislabel_severity(true_severity: str, reliability: float) -> str:
    if random.random() < reliability + 0.15:
        return SEVERITY_PLAYER_LABELS.get(true_severity, true_severity)
    # Under- or over-state severity
    order = ["low", "medium", "high", "critical"]
    try:
        idx = order.index(true_severity)
    except ValueError:
        return "невизначено"
    shift = random.choice([-1, 1]) if random.random() < 0.5 else 0
    return SEVERITY_PLAYER_LABELS.get(order[max(0, min(3, idx + shift))], "невизначено")


def _distort_region_name(true_region: str, reliability: float, all_regions: list[Region]) -> str:
    if random.random() < reliability or not all_regions:
        return true_region
    decoy = random.choice([r.name for r in all_regions if r.name != true_region])
    return f"{decoy} {random.choice(WRONG_REGION_SUFFIXES)}"


def _distort_country(true_country: str, reliability: float) -> str:
    if random.random() < reliability + 0.1:
        return true_country
    qualifiers = ["ймовірна", "непідтверджена", "можлива"]
    return f"{random.choice(qualifiers)} активність за участю {true_country}"


def _jitter_coordinates(lat: float, lng: float, error_deg: float) -> tuple[float, float]:
    return (
        lat + random.uniform(-error_deg, error_deg),
        lng + random.uniform(-error_deg, error_deg),
    )


def compute_display_confidence(profile: SourceProfile, content_accuracy: float) -> int:
    """Confidence shown to the player — intentionally uncorrelated with truth."""
    base = random.randint(28, 88)
    if profile.code in ("SATINT", "CYBER"):
        base += random.randint(0, 12)
    if profile.code == "HUMINT":
        base += random.randint(-8, 18)
    # High confidence can still accompany inaccurate content.
    if random.random() < 0.25:
        base = random.randint(70, 96)
    elif random.random() < 0.2:
        base = random.randint(22, 45)
    return max(5, min(99, base))


def distort_event_for_source(
    event: Event,
    profile: SourceProfile,
    all_regions: list[Region],
) -> DistortedReportContent:
    reliability = profile.detail_reliability
    if event.event_type in profile.preferred_event_types:
        reliability = min(0.95, reliability + 0.18)

    activity = _mislabel_event_type(event.event_type, reliability)
    severity_word = _mislabel_severity(event.severity, reliability)
    region_display = _distort_region_name(event.region_name, reliability, all_regions)
    country_display = _distort_country(event.country_name, reliability)

    lat, lng = _jitter_coordinates(
        event.latitude,
        event.longitude,
        profile.location_error_deg,
    )

    location_error = abs(lat - event.latitude) + abs(lng - event.longitude)
    location_accuracy = max(0.0, 1.0 - (location_error / (profile.location_error_deg * 2 + 0.01)))

    content_errors = 0
    if region_display != event.region_name:
        content_errors += 1
    if activity != EVENT_TYPE_PLAYER_LABELS.get(event.event_type, event.event_type):
        content_errors += 1
    if severity_word != SEVERITY_PLAYER_LABELS.get(event.severity, event.severity):
        content_errors += 1
    content_accuracy = max(0.05, 1.0 - content_errors * 0.35)

    title = f"{profile.title_prefix}: {severity_word} {activity} — {region_display}"

    if profile.code == "SATINT":
        description = (
            f"Знімки вказують на {activity} поблизу {region_display}. "
            f"Оцінка: {severity_word} пріоритет. Причетність {country_display} не підтверджено."
        )
    elif profile.code == "SIGINT":
        description = (
            f"Перехоплений трафік відповідає ознакам: {activity} у районі {region_display}. "
            f"Геолокація приблизна. Зв’язок із {country_display} не підтверджено."
        )
    elif profile.code == "HUMINT":
        description = (
            f"Джерело повідомляє про {activity}, що впливає на {region_display}. "
            f"Деталі суперечать іншим даним. {country_display} — "
            "вважати інформацією з одного джерела."
        )
    else:  # CYBER
        description = (
            f"Мережева телеметрія вказує на {activity} з осередком поблизу {region_display}. "
            f"Можливий зв’язок з інфраструктурою {country_display} — це припущення."
        )

    if reliability < 0.55 and random.random() < 0.4:
        description += " Попередні оцінки в цьому районі можуть бути хибними."

    confidence = compute_display_confidence(profile, content_accuracy)

    return DistortedReportContent(
        title=title[:255],
        description=description,
        region_name=region_display,
        latitude=lat,
        longitude=lng,
        confidence=confidence,
        content_accuracy=content_accuracy,
        location_accuracy=location_accuracy,
    )


def generate_phantom_content(
    region: Region,
    profile: SourceProfile,
    all_regions: list[Region],
) -> DistortedReportContent:
    """False-positive style report with no underlying ground-truth event."""
    activity = random.choice(WRONG_TYPE_LABELS)
    region_display = _distort_region_name(region.name, 0.3, all_regions)
    lat, lng = _jitter_coordinates(
        region.latitude, region.longitude, profile.location_error_deg * 1.5
    )
    confidence = compute_display_confidence(profile, 0.2)

    return DistortedReportContent(
        title=f"{profile.title_prefix}: Непідтверджена активність: {activity} — {region_display}",
        description=(
            f"Збір даних виявив ознаки: {activity} поблизу {region_display}. "
            "Наразі підтверджень з інших джерел немає. "
            "Це може бути безпечною або оманливою активністю."
        ),
        region_name=region_display,
        latitude=lat,
        longitude=lng,
        confidence=confidence,
        content_accuracy=random.uniform(0.0, 0.25),
        location_accuracy=random.uniform(0.1, 0.4),
    )
