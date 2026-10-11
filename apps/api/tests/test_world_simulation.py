from fastapi.testclient import TestClient

from prisma_api.core.database import SessionLocal
from prisma_api.features.analysts.seed import DEFAULT_ANALYSTS
from prisma_api.features.operations.seed_assets import DEFAULT_ASSETS
from prisma_api.features.world.seed import ensure_world
from prisma_api.features.world.simulation import WorldSimulationService
from prisma_api.models import ASSET_AVAILABLE, City, Country, Event, Region


def test_world_seeded_with_geography() -> None:
    db = SessionLocal()
    try:
        world = ensure_world(db)
        countries = db.query(Country).filter(Country.world_id == world.id).all()
        regions = db.query(Region).count()
        cities = db.query(City).count()
        assert len(countries) >= 10
        assert regions >= 10
        assert cities >= 10
    finally:
        db.close()


def test_tick_advances_clock_and_can_generate_events(client: TestClient) -> None:
    db = SessionLocal()
    try:
        world = ensure_world(db)
        world.game_minutes = 0
        world.ticks_elapsed = 0
        db.query(Event).filter(Event.world_id == world.id).delete()
        db.commit()

        service = WorldSimulationService(db)
        generated_any = False
        for _ in range(20):
            result = service.run_single_tick()
            assert result.world.game_minutes > 0
            if result.new_events:
                generated_any = True
                break
        assert generated_any, "Expected at least one geopolitical event within 20 ticks"
    finally:
        db.close()


def test_world_state_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/world/state")
    assert response.status_code == 200
    data = response.json()
    assert "clock" in data
    assert "events" in data
    assert data["clock"]["tick_game_minutes"] == 15
    assert data["events"], "A new game must always expose an opening event"
    assert data["intel_reports"], "A new game must always expose an opening intelligence report"


def test_reset_starts_a_clean_playable_world(client: TestClient) -> None:
    client.post("/api/v1/world/advance", json={"minutes": 60})
    response = client.post("/api/v1/world/reset")
    assert response.status_code == 200
    data = response.json()
    assert data["clock"]["game_minutes"] == 0
    assert data["clock"]["is_paused"] is True
    assert len(data["events"]) == 1
    assert len(data["intel_reports"]) == 1


def test_reset_restores_default_roster_and_clears_in_progress_work(client: TestClient) -> None:
    client.post("/api/v1/world/advance", json={"minutes": 60})
    intel = client.get("/api/v1/intelligence/reports").json()
    assets = client.get("/api/v1/operations/assets").json()
    recon_asset = next(a for a in assets if a["supports_recon"] and a["status"] == ASSET_AVAILABLE)
    plan_response = client.post(
        "/api/v1/operations/plan",
        json={
            "operation_type": "recon",
            "intel_report_id": intel[0]["id"],
            "asset_id": recon_asset["id"],
        },
    )
    assert plan_response.status_code == 200

    response = client.post("/api/v1/world/reset")
    assert response.status_code == 200
    data = response.json()

    assert len(data["assets"]) == len(DEFAULT_ASSETS)
    assert all(a["status"] == ASSET_AVAILABLE for a in data["assets"]), (
        "the busy asset from the pre-reset operation must come back available"
    )
    assert data["operations"] == [], "a fresh world must not carry over the old operation"

    analysts = client.get("/api/v1/analysts").json()
    assert len(analysts) == len(DEFAULT_ANALYSTS)


def test_advance_endpoint(client: TestClient) -> None:
    response = client.post("/api/v1/world/advance", json={"minutes": 60})
    assert response.status_code == 200
    data = response.json()
    assert data["ticks_run"] == 4
    assert len(data["events"]) >= 0
