"""Seed countries, regions, cities, and the opening training situation."""

import uuid

from sqlalchemy.orm import Session

from prisma_api.features.world.constants import (
    BLOC_ASTER,
    BLOC_CONSORTIUM,
    BLOC_NEUTRAL,
    BLOC_NORDEX,
)
from prisma_api.models import (
    Analyst,
    AnalystAssessment,
    Asset,
    City,
    Country,
    Event,
    IntelligenceAction,
    IntelligenceReport,
    Operation,
    OperationResult,
    Region,
    World,
    WorldTick,
)

# country_code -> (name, bloc, regions[(name, lat, lng, cities[(name, lat, lng)])])
WORLD_GEOGRAPHY: dict[str, tuple[str, str, list]] = {
    "AST-CAS": (
        "Каскадійський технат",
        BLOC_ASTER,
        [
            (
                "Тихоокеанський північно-західний коридор",
                47.6,
                -122.3,
                [("Сіетлська аркологія", 47.61, -122.33), ("Ванкуверський вузол", 49.28, -123.12)],
            ),
        ],
    ),
    "AST-BAL": (
        "Балтійські держави-стражі",
        BLOC_ASTER,
        [
            (
                "Балтійський коридор",
                56.9,
                24.1,
                [("Ризьке командування", 56.95, 24.11), ("Талліннський ретранслятор", 59.44, 24.75)],
            ),
        ],
    ),
    "AST-KJP": (
        "Корейсько-японський кіберпакт",
        BLOC_ASTER,
        [
            (
                "Мережа Східного моря",
                35.7,
                139.7,
                [("Токійський аплінк", 35.68, 139.69), ("Пусанський шлюз", 35.18, 129.08)],
            ),
        ],
    ),
    "NDX-CORE": (
        "Метрополійне ядро Nordex",
        BLOC_NORDEX,
        [
            (
                "Рейнський промисловий пояс",
                51.2,
                6.8,
                [("Кельнський арсенал", 50.94, 6.96), ("Роттердамський порт", 51.92, 4.48)],
            ),
            (
                "Крайня Північ",
                63.4,
                10.4,
                [("Тронгеймська база", 63.43, 10.39)],
            ),
        ],
    ),
    "NDX-ATL": (
        "Атлантичний оборонний договір",
        BLOC_NORDEX,
        [
            (
                "Східне узбережжя",
                38.9,
                -77.0,
                [("Норфолкська ударна група", 36.85, -76.29), ("Галіфакська станція", 44.65, -63.58)],
            ),
        ],
    ),
    "NDX-ARC": (
        "Територія Арктичного щита",
        BLOC_NORDEX,
        [
            (
                "Баренцовий рубіж",
                69.6,
                19.0,
                [("Тромсенський пост", 69.65, 18.96)],
            ),
        ],
    ),
    "CON-CEN": (
        "Центральна влада консорціуму",
        BLOC_CONSORTIUM,
        [
            (
                "Серце Центральної Азії",
                41.3,
                69.2,
                [("Ташкентський вузол", 41.30, 69.24), ("Алматинська логістика", 43.24, 76.95)],
            ),
        ],
    ),
    "CON-PIB": (
        "Перський промисловий пояс",
        BLOC_CONSORTIUM,
        [
            (
                "Виробнича зона затоки",
                26.2,
                50.6,
                [("Даммамський комплекс", 26.42, 50.09), ("Майданчик Бендер-Аббас", 27.18, 56.28)],
            ),
        ],
    ),
    "CON-ASE": (
        "Виробничий коридор АСЕАН",
        BLOC_CONSORTIUM,
        [
            (
                "Виробничий пояс Південного Китаю",
                12.0,
                114.0,
                [("Манільське виробництво", 14.60, 120.98), ("Підприємства Хошиміна", 10.82, 106.63)],
            ),
        ],
    ),
    "NEU-IST": (
        "Вільна держава Стамбулської протоки",
        BLOC_NEUTRAL,
        [
            (
                "Босфорська протока",
                41.0,
                29.0,
                [("Стамбульський коридор", 41.01, 28.98)],
            ),
        ],
    ),
    "NEU-SAH": (
        "Буферна держава Сахелю",
        BLOC_NEUTRAL,
        [
            (
                "Транссахельський транзит",
                13.5,
                2.1,
                [("Перехід Ніамей", 13.51, 2.11)],
            ),
        ],
    ),
}


def seed_world(db: Session) -> World:
    world = World(
        name="Криза PRISMA 2035",
        crisis_start_label="14 БЕР 2035 0600Z",
        game_minutes=0,
        is_paused=True,
        speed=1,
    )
    db.add(world)
    db.flush()

    for code, (country_name, bloc, regions_data) in WORLD_GEOGRAPHY.items():
        country = Country(
            world_id=world.id,
            code=code,
            name=country_name,
            bloc=bloc,
        )
        db.add(country)
        db.flush()

        for region_name, r_lat, r_lng, cities_data in regions_data:
            region = Region(
                country_id=country.id,
                name=region_name,
                latitude=r_lat,
                longitude=r_lng,
            )
            db.add(region)
            db.flush()

            for city_name, c_lat, c_lng in cities_data:
                db.add(
                    City(
                        region_id=region.id,
                        name=city_name,
                        latitude=c_lat,
                        longitude=c_lng,
                    )
                )

    _ensure_opening_brief(db, world)
    db.commit()
    db.refresh(world)
    return world


def ensure_world(db: Session) -> World:
    world = db.query(World).first()
    if world is not None:
        _ensure_opening_brief(db, world)
        db.commit()
        return world
    return seed_world(db)


def reset_world(db: Session) -> World:
    """Replace the local single-player campaign with a clean opening scenario."""
    db.query(OperationResult).delete(synchronize_session=False)
    db.query(Operation).delete(synchronize_session=False)
    db.query(AnalystAssessment).delete(synchronize_session=False)
    db.query(IntelligenceReport).update(
        {IntelligenceReport.requested_by_action_id: None}, synchronize_session=False
    )
    db.query(IntelligenceAction).delete(synchronize_session=False)
    db.query(IntelligenceReport).delete(synchronize_session=False)
    db.query(Event).delete(synchronize_session=False)
    db.query(WorldTick).delete(synchronize_session=False)
    db.query(Analyst).delete(synchronize_session=False)
    db.query(Asset).delete(synchronize_session=False)
    db.query(City).delete(synchronize_session=False)
    db.query(Region).delete(synchronize_session=False)
    db.query(Country).delete(synchronize_session=False)
    db.query(World).delete(synchronize_session=False)
    db.commit()
    return seed_world(db)


def _ensure_opening_brief(db: Session, world: World) -> None:
    """Provide a guaranteed first signal so a new player can start the tutorial."""
    region = db.query(Region).filter(Region.name == "Балтійський коридор").first()
    if region is None:
        return

    opening_event = (
        db.query(Event)
        .filter(Event.world_id == world.id, Event.event_type == "tutorial_signal")
        .first()
    )
    if opening_event is None:
        opening_event = Event(
            id=str(uuid.uuid4()),
            world_id=world.id,
            tick_number=0,
            game_minutes=world.game_minutes,
            event_type="tutorial_signal",
            severity="medium",
            title="Незвична активність — Балтійський коридор",
            summary=(
                "Спостережні пости зафіксували невстановлені переміщення біля критичної "
                "інфраструктури. Причину активності ще не визначено."
            ),
            region_id=region.id,
            region_name=region.name,
            country_name=region.country.name,
            latitude=region.latitude,
            longitude=region.longitude,
        )
        db.add(opening_event)
        db.flush()

    has_opening_intel = (
        db.query(IntelligenceReport)
        .filter(IntelligenceReport.world_id == world.id, IntelligenceReport.related_event_id == opening_event.id)
        .first()
    )
    if has_opening_intel is None:
        db.add(
            IntelligenceReport(
                id=str(uuid.uuid4()),
                world_id=world.id,
                game_minutes=world.game_minutes,
                source="SIGINT",
                confidence=62,
                title="SIGINT: Незвична активність — Балтійський коридор",
                summary=(
                    "Перехоплений трафік свідчить про зміну режиму зв’язку в районі. "
                    "Джерело оцінює загрозу як помірну; потрібна додаткова перевірка."
                ),
                region_name=region.name,
                latitude=region.latitude,
                longitude=region.longitude,
                related_event_id=opening_event.id,
                content_accuracy=0.72,
                location_accuracy=0.88,
            )
        )
