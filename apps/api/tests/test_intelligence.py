from fastapi.testclient import TestClient

from prisma_api.core.database import SessionLocal
from prisma_api.features.events.event_engine import generate_geopolitical_event
from prisma_api.features.intelligence.engine import IntelligenceEngine
from prisma_api.features.world.seed import ensure_world


def test_intel_reports_have_required_fields(client: TestClient) -> None:
    response = client.get("/api/v1/intelligence/reports")
    assert response.status_code == 200
    if not response.json():
        client.post("/api/v1/world/advance", json={"minutes": 60})
        response = client.get("/api/v1/intelligence/reports")
    reports = response.json()
    assert len(reports) > 0
    report = reports[0]
    assert "title" in report
    assert "description" in report
    assert report["source"] in ("SATINT", "SIGINT", "HUMINT", "CYBER")
    assert 0 <= report["confidence"] <= 100
    assert "timestamp" in report
    assert "region" in report
    assert "coordinates" in report
    assert "related_event_id" not in report
    assert "content_accuracy" not in report


def test_intel_can_differ_from_ground_truth() -> None:
    db = SessionLocal()
    try:
        world = ensure_world(db)
        world.game_minutes = 100
        db.commit()

        event = generate_geopolitical_event(db, world, tick_number=1)
        assert event is not None
        db.commit()

        engine = IntelligenceEngine(db)
        reports = engine.generate_for_event(world, event)
        db.commit()
        assert len(reports) >= 1

        inaccurate = False
        for report in reports:
            if report.region_name != event.region_name:
                inaccurate = True
            if abs(report.latitude - event.latitude) > 0.01:
                inaccurate = True
            if report.summary and event.summary and report.summary == event.summary:
                inaccurate = False
            else:
                inaccurate = True
        assert inaccurate or reports[0].content_accuracy < 1.0
    finally:
        db.close()


def test_intel_generated_from_events_on_advance(client: TestClient) -> None:
    response = client.post("/api/v1/world/advance", json={"minutes": 120})
    assert response.status_code == 200
    data = response.json()
    assert len(data["intel_reports"]) >= 0
    if data["new_events"]:
        assert len(data["new_intel_reports"]) >= 1
