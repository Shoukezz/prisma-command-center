import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

test_db = Path(tempfile.gettempdir()) / f"prisma-api-tests-{os.getpid()}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{test_db}"
os.environ["ENVIRONMENT"] = "test"

from prisma_api.core.database import init_db  # noqa: E402
from prisma_api.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def reset_database() -> None:
    init_db()


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
