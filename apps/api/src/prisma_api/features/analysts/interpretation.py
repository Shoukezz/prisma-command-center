"""Generate analyst-specific interpretations of intelligence reports."""

from __future__ import annotations

import random
from dataclasses import dataclass

from prisma_api.features.analysts.constants import (
    BIAS_CYBER_FOCUS,
    BIAS_DIPLOMATIC,
    BIAS_HAWKISH,
    BIAS_SKEPTICAL,
    BIAS_TECH_OPTIMIST,
    SOURCE_SPECIALTY_AFFINITY,
)
from prisma_api.models import Analyst, IntelligenceReport

SPECIALTY_LABELS = {
    "satellite_imagery": "Супутникові знімки",
    "signals_intelligence": "Сигнальна розвідка",
    "cyber_threats": "Кіберзагрози",
    "human_source": "Людські джерела",
    "kinetic_operations": "Кінетичні операції",
    "regional_affairs": "Регіональні справи",
}

BIAS_LABELS = {
    BIAS_HAWKISH: "Прихильник силових дій",
    BIAS_SKEPTICAL: "Скептик",
    BIAS_CYBER_FOCUS: "Кіберфокус",
    BIAS_DIPLOMATIC: "Дипломат",
    BIAS_TECH_OPTIMIST: "Технооптиміст",
}


@dataclass
class InterpretationResult:
    assessment: str
    assessed_confidence: int


def _specialty_match(report: IntelligenceReport, analyst: Analyst) -> bool:
    affinity = SOURCE_SPECIALTY_AFFINITY.get(report.source)
    return affinity == analyst.specialty


def _bias_confidence_delta(bias: str) -> int:
    if bias == BIAS_HAWKISH:
        return random.randint(8, 22)
    if bias == BIAS_SKEPTICAL:
        return random.randint(-22, -6)
    if bias == BIAS_DIPLOMATIC:
        return random.randint(-15, -3)
    if bias == BIAS_CYBER_FOCUS:
        return random.randint(5, 15) if random.random() < 0.5 else random.randint(-8, 5)
    if bias == BIAS_TECH_OPTIMIST:
        return random.randint(-10, 8)
    return random.randint(-5, 5)


def _bias_narrative(bias: str, report: IntelligenceReport) -> str:
    region = report.region_name
    if bias == BIAS_HAWKISH:
        return (
            f"Рекомендую підвищити рівень готовності щодо {region}. "
            "Планування найгіршого сценарію виправдане, навіть якщо первинні дані неоднозначні."
        )
    if bias == BIAS_SKEPTICAL:
        return (
            f"Вважайте дані щодо {region} непідтвердженими до незалежної верифікації. "
            "Найбільше занепокоєння викликає надійність ланцюга джерел."
        )
    if bias == BIAS_DIPLOMATIC:
        return (
            f"Раджу обережність перед будь-якою силовою відповіддю поблизу {region}. "
            "Ескалація може бути спричинена внутрішніми, а не зовнішніми чинниками."
        )
    if bias == BIAS_CYBER_FOCUS:
        return (
            f"Пріоритетними є кібернетичні та інформаційні вектори навколо {region}. "
            "Фізичні індикатори можуть бути другорядними порівняно з мережевою активністю."
        )
    if bias == BIAS_TECH_OPTIMIST:
        return (
            f"Артефакти збору даних поблизу {region} можуть відображати рутинну активність. "
            "Технічний шум часто помилково сприймають як ворожі наміри."
        )
    return f"До даних щодо {region} застосовано стандартну перевірку; виняткових чинників не виявлено."


def interpret_report(report: IntelligenceReport, analyst: Analyst) -> InterpretationResult:
    """Produce a distinct analyst reading — may diverge from raw report confidence."""
    base = report.confidence
    delta = _bias_confidence_delta(analyst.bias)

    if _specialty_match(report, analyst):
        delta += random.randint(3, 12)
    else:
        delta += random.randint(-12, 4)

    # Reliability: higher reliability tends toward measured adjustment; low reliability swings wild.
    if analyst.reliability >= 0.7:
        delta = int(delta * 0.75)
    elif analyst.reliability < 0.6:
        if random.random() < 0.35:
            delta += random.choice([-25, 25])

    assessed = max(5, min(99, base + delta))

    specialty_label = SPECIALTY_LABELS.get(analyst.specialty, analyst.specialty)
    bias_label = BIAS_LABELS.get(analyst.bias, analyst.bias)
    narrative = _bias_narrative(analyst.bias, report)

    assessment = (
        f"[{specialty_label} / {bias_label}] {narrative} "
        f"Моя оцінка ймовірності: {assessed}% (збір даних повідомив {base}%)."
    )

    return InterpretationResult(assessment=assessment, assessed_confidence=assessed)
