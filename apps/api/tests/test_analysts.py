from fastapi.testclient import TestClient

from prisma_api.core.database import SessionLocal
from prisma_api.features.analysts.interpretation import interpret_report
from prisma_api.features.analysts.seed import seed_analysts
from prisma_api.features.analysts.service import AnalystService
from prisma_api.features.world.seed import ensure_world
from prisma_api.features.world.simulation import WorldSimulationService


def test_analysts_seeded(client: TestClient) -> None:
    response = client.get("/api/v1/analysts")
    assert response.status_code == 200
    analysts = response.json()
    assert len(analysts) >= 5
    first = analysts[0]
    assert "specialty" in first
    assert "reliability" in first
    assert "bias" in first
    assert 0 <= first["reliability"] <= 1


def test_intel_reports_include_assessments(client: TestClient) -> None:
    client.post("/api/v1/world/advance", json={"minutes": 90})
    reports = client.get("/api/v1/intelligence/reports").json()
    assert reports
    report_with_assessments = next((r for r in reports if r["analyst_assessments"]), None)
    assert report_with_assessments is not None
    assessment = report_with_assessments["analyst_assessments"][0]
    assert "analyst_name" in assessment
    assert "assessment" in assessment
    assert "assessed_confidence" in assessment
    assert "specialty" in assessment
    assert "bias" in assessment
    assert "reliability" in assessment


def test_analysts_interpret_differently() -> None:
    db = SessionLocal()
    try:
        world = ensure_world(db)
        seed_analysts(db, world)
        WorldSimulationService(db).advance_minutes(60)
        intel = WorldSimulationService(db).list_intel()
        if not intel:
            return
        report = intel[0]
        roster = AnalystService(db).list_analysts()
        results = [interpret_report(report, a) for a in roster[:3]]
        confidences = {r.assessed_confidence for r in results}
        texts = {r.assessment for r in results}
        assert len(confidences) >= 2
        assert len(texts) == 3
    finally:
        db.close()
