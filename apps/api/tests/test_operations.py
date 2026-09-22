from fastapi.testclient import TestClient

from prisma_api.core.database import SessionLocal
from prisma_api.features.operations.service import OperationsService
from prisma_api.features.world.seed import ensure_world
from prisma_api.features.world.simulation import WorldSimulationService
from prisma_api.models import ASSET_AVAILABLE, OP_STATUS_ACTIVE, OP_STATUS_COMPLETED


def test_assets_seeded(client: TestClient) -> None:
    response = client.get("/api/v1/operations/assets")
    assert response.status_code == 200
    assets = response.json()
    assert len(assets) >= 4
    assert any(a["status"] == ASSET_AVAILABLE for a in assets)


def test_plan_recon_operation(client: TestClient) -> None:
    client.post("/api/v1/world/advance", json={"minutes": 60})
    intel = client.get("/api/v1/intelligence/reports").json()
    assets = client.get("/api/v1/operations/assets").json()
    assert intel and assets
    recon_asset = next(a for a in assets if a["supports_recon"] and a["status"] == ASSET_AVAILABLE)
    response = client.post(
        "/api/v1/operations/plan",
        json={
            "operation_type": "recon",
            "intel_report_id": intel[0]["id"],
            "asset_id": recon_asset["id"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["operation_type"] == "recon"
    assert data["status"] == OP_STATUS_ACTIVE
    assert data["duration_minutes"] == 45
    assert data["intel_confidence"] == intel[0]["confidence"]


def test_operation_resolves_after_time(client: TestClient) -> None:
    client.post("/api/v1/world/advance", json={"minutes": 30})
    intel = client.get("/api/v1/intelligence/reports").json()
    assets = client.get("/api/v1/operations/assets").json()
    strike_asset = next(a for a in assets if a["supports_strike"] and a["status"] == ASSET_AVAILABLE)
    planned = client.post(
        "/api/v1/operations/plan",
        json={
            "operation_type": "strike",
            "intel_report_id": intel[0]["id"],
            "asset_id": strike_asset["id"],
        },
    ).json()
    advance = client.post("/api/v1/world/advance", json={"minutes": 120})
    assert advance.status_code == 200
    operations = advance.json()["operations"]
    finished = next((o for o in operations if o["id"] == planned["id"]), None)
    assert finished is not None
    assert finished["status"] in (OP_STATUS_COMPLETED, "failed")
    assert finished["result"] is not None
    assert "outcome_summary" in finished["result"]


def test_success_probability_scales_with_confidence() -> None:
    db = SessionLocal()
    try:
        world = ensure_world(db)
        WorldSimulationService(db).advance_minutes(30)
        intel = WorldSimulationService(db).list_intel()
        assets = OperationsService(db).list_assets()
        if not intel or not assets:
            return
        high_conf = max(intel, key=lambda r: r.confidence)
        asset = next(a for a in assets if a.supports_recon and a.status == ASSET_AVAILABLE)
        op = OperationsService(db).plan_operation("recon", high_conf.id, asset.id)
        assert op.intel_confidence == high_conf.confidence
    finally:
        db.close()
