"""Resolve completed operations into player-visible outcomes."""

from __future__ import annotations

import random
import uuid

from sqlalchemy.orm import Session

from prisma_api.features.operations.constants import (
    ACCURACY_WEIGHT,
    CONFIDENCE_WEIGHT,
    TYPE_SUCCESS_MODIFIER,
)
from prisma_api.models import (
    ASSET_AVAILABLE,
    ASSET_DAMAGED,
    ASSET_DESTROYED,
    Event,
    OP_STATUS_COMPLETED,
    OP_STATUS_FAILED,
    OPERATION_RECON,
    OPERATION_STRIKE,
    Asset,
    IntelligenceReport,
    Operation,
    OperationResult,
    World,
)


def _success_probability(
    operation_type: str,
    intel_confidence: int,
    content_accuracy: float,
) -> float:
    confidence_factor = max(0.05, min(1.0, intel_confidence / 100.0))
    accuracy_factor = max(0.05, min(1.0, content_accuracy))
    blended = confidence_factor * CONFIDENCE_WEIGHT + accuracy_factor * ACCURACY_WEIGHT
    return max(0.08, min(0.95, blended * TYPE_SUCCESS_MODIFIER[operation_type]))


def _outcome_text(operation: Operation, success: bool) -> str:
    region = operation.region_name
    if operation.operation_type == OPERATION_RECON:
        if success:
            return (
                f"Розвідку над {region} завершено. Пакети зібраних даних доставлено; "
                "додаткові звіти очікуються в наступному циклі."
            )
        return (
            f"Розвідка над {region} не вдалася. Ресурс перервав місію через спірний повітряний простір "
            "або неточні координати — достовірність цілі невизначена."
        )
    if success:
        return (
            f"Ударна група по цілях поблизу {region} повідомляє про завершення місії. "
            "Оцінка бойових пошкоджень триває; початкові показники позитивні."
        )
    return (
        f"Удар поблизу {region} був невдалим. Ціль слабо відповідала розвідданим "
        f"(достовірність під час планування — {operation.intel_confidence}%) — рекомендуємо новий збір даних."
    )


def _apply_asset_aftermath(asset: Asset, operation_type: str, success: bool) -> None:
    if success:
        asset.status = ASSET_AVAILABLE
        return
    if operation_type == OPERATION_STRIKE:
        roll = random.random()
        if roll < 0.15:
            asset.status = ASSET_DESTROYED
        elif roll < 0.45:
            asset.status = ASSET_DAMAGED
        else:
            asset.status = ASSET_AVAILABLE
    else:
        if random.random() < 0.2:
            asset.status = ASSET_DAMAGED
        else:
            asset.status = ASSET_AVAILABLE


def _generate_consequences(
    db: Session,
    world: World,
    operation: Operation,
    intel: IntelligenceReport,
    success: bool,
) -> None:
    """Generate follow-up intelligence and/or events based on operation outcome."""

    if operation.operation_type == OPERATION_RECON:
        if success:
            # Successful recon generates detailed follow-up intelligence
            follow_up = IntelligenceReport(
                id=str(uuid.uuid4()),
                world_id=world.id,
                game_minutes=world.game_minutes + random.randint(5, 15),
                source="COLLECTION_ASSET",
                confidence=min(98, intel.confidence + random.randint(10, 20)),
                title=f"Розвідувальний звіт: {intel.title}",
                summary=(
                    f"Ресурс збору даних над {intel.region_name} успішно завершив завдання. "
                    f"Отримано детальні знімки та сигнальну розвідку цільового району. "
                    f"Характер активності відповідає початковій оцінці. Уточнення координат: "
                    f"±{random.choice(['50m', '100m', '200m'])}."
                ),
                region_name=intel.region_name,
                latitude=intel.latitude + random.uniform(-0.05, 0.05),
                longitude=intel.longitude + random.uniform(-0.05, 0.05),
                related_event_id=intel.related_event_id,
                content_accuracy=min(0.95, intel.content_accuracy + random.uniform(0.1, 0.2)),
                location_accuracy=min(0.95, intel.location_accuracy + random.uniform(0.15, 0.25)),
            )
            db.add(follow_up)
        else:
            # Failed recon creates ambiguity event: asset aborted, confidence in error
            bad_intel_event = Event(
                id=str(uuid.uuid4()),
                world_id=world.id,
                tick_number=world.ticks_elapsed,
                game_minutes=world.game_minutes,
                event_type="intelligence_failure",
                severity="medium",
                title=f"Прогалина в даних: {intel.title}",
                summary=(
                    f"Заплановану розвідку {intel.region_name} скасовано. "
                    f"Цільовий район спірний або дані локації пошкоджено. "
                    f"Достовірність початкового звіту під сумнівом. Рекомендуємо новий збір даних."
                ),
                region_name=intel.region_name,
                country_name=intel.region_name,
                latitude=intel.latitude,
                longitude=intel.longitude,
            )
            db.add(bad_intel_event)

    elif operation.operation_type == OPERATION_STRIKE:
        if success:
            # Successful strike creates a new escalation event in the region
            escalation_event = Event(
                id=str(uuid.uuid4()),
                world_id=world.id,
                tick_number=world.ticks_elapsed,
                game_minutes=world.game_minutes,
                event_type="military_strike_consequence",
                severity="critical" if random.random() < 0.4 else "high",
                title=f"Наслідки удару: {intel.region_name}",
                summary=(
                    f"Військовий удар поблизу {intel.region_name} спричинив каскадні наслідки. "
                    f"Регіональна напруженість зростає. Відбувається обмін дипломатичними сигналами. "
                    f"Ризик дій у відповідь підвищено."
                ),
                region_name=intel.region_name,
                country_name=intel.region_name,
                latitude=intel.latitude + random.uniform(-0.2, 0.2),
                longitude=intel.longitude + random.uniform(-0.2, 0.2),
            )
            db.add(escalation_event)

            # Generate follow-up recon to assess damage
            damage_report = IntelligenceReport(
                id=str(uuid.uuid4()),
                world_id=world.id,
                game_minutes=world.game_minutes + random.randint(20, 40),
                source="POST_STRIKE_BDA",
                confidence=random.randint(65, 85),
                title=f"Оцінка бойових пошкоджень: {intel.region_name}",
                summary=(
                    f"Післяударний збір даних вказує на значний вплив у цільовій зоні. "
                    f"Попередня оцінка свідчить про виконання цілей місії. "
                    f"Повний аналіз пошкоджень триває."
                ),
                region_name=intel.region_name,
                latitude=intel.latitude + random.uniform(-0.1, 0.1),
                longitude=intel.longitude + random.uniform(-0.1, 0.1),
                related_event_id=intel.related_event_id,
                content_accuracy=min(0.85, intel.content_accuracy + random.uniform(0.05, 0.15)),
                location_accuracy=min(0.90, intel.location_accuracy + random.uniform(0.1, 0.2)),
            )
            db.add(damage_report)
        else:
            # Failed strike: weapon miss, poor intelligence, creates diplomatic crisis
            failed_strike_event = Event(
                id=str(uuid.uuid4()),
                world_id=world.id,
                tick_number=world.ticks_elapsed,
                game_minutes=world.game_minutes,
                event_type="strike_failure_crisis",
                severity="critical",
                title=f"Наслідки невдалого удару: {intel.region_name}",
                summary=(
                    f"Військовий удар поблизу {intel.region_name} пішов не за планом. "
                    f"Повідомляють про значні жертви серед цивільних або повний промах по цілі. "
                    f"Міжнародна дипломатична реакція неминуча. Імовірна політична криза."
                ),
                region_name=intel.region_name,
                country_name=intel.region_name,
                latitude=intel.latitude + random.uniform(-0.3, 0.3),
                longitude=intel.longitude + random.uniform(-0.3, 0.3),
            )
            db.add(failed_strike_event)

            # Intelligence shows we were wrong
            correction_intel = IntelligenceReport(
                id=str(uuid.uuid4()),
                world_id=world.id,
                game_minutes=world.game_minutes + random.randint(10, 25),
                source="SIGINT_CORRECTION",
                confidence=random.randint(50, 70),
                title=f"Уточнення розвідданих: {intel.title}",
                summary=(
                    f"Додатковий збір даних вказує, що початкова оцінка цілі була "
                    f"суттєво неточною. Фактична активність відрізняється від прогнозу. "
                    f"Рекомендуємо повністю переглянути методику збору даних."
                ),
                region_name=intel.region_name,
                latitude=intel.latitude + random.uniform(-0.2, 0.2),
                longitude=intel.longitude + random.uniform(-0.2, 0.2),
                related_event_id=intel.related_event_id,
                content_accuracy=max(0.3, intel.content_accuracy - random.uniform(0.1, 0.2)),
                location_accuracy=max(0.3, intel.location_accuracy - random.uniform(0.1, 0.2)),
            )
            db.add(correction_intel)


def resolve_operation(
    db: Session,
    operation: Operation,
    intel: IntelligenceReport,
) -> OperationResult:
    probability = _success_probability(
        operation.operation_type,
        operation.intel_confidence,
        intel.content_accuracy,
    )
    success = random.random() < probability
    summary = _outcome_text(operation, success)

    operation.status = OP_STATUS_COMPLETED if success else OP_STATUS_FAILED
    _apply_asset_aftermath(operation.asset, operation.operation_type, success)

    result = OperationResult(
        id=str(uuid.uuid4()),
        operation_id=operation.id,
        success=success,
        outcome_summary=summary,
        confidence_at_planning=operation.intel_confidence,
        completed_at=operation.completes_at,
    )
    db.add(result)

    # Generate consequences: follow-up intelligence and/or events
    world = db.query(World).filter(World.id == operation.world_id).first()
    if world is not None:
        _generate_consequences(db, world, operation, intel, success)

    return result
