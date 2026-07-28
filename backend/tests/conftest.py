import os

import pytest
from fastapi.testclient import TestClient
from qdrant_client import QdrantClient

from app.config import settings
from app.main import app

_TEST_COLLECTION = "documents_test"
_TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_app.db")


@pytest.fixture(autouse=True, scope="session")
def _use_isolated_test_collection() -> None:
    # Tests that exercise the real ingestion pipeline write real vectors to
    # Qdrant, and real rows to SQLite — point both at dedicated test-only
    # locations so test runs never mix with (or pollute) whatever a developer
    # is exploring against the same services during manual testing.
    settings.qdrant_collection = _TEST_COLLECTION
    settings.database_path = _TEST_DB_PATH

    # Drop any leftovers from a previous run so each session starts from a
    # known-empty collection — otherwise accumulated fixture data from past
    # runs can pad out top-k search results and produce order-dependent flakes.
    client = QdrantClient(url=settings.qdrant_url)
    if client.collection_exists(_TEST_COLLECTION):
        client.delete_collection(_TEST_COLLECTION)

    if os.path.exists(_TEST_DB_PATH):
        os.remove(_TEST_DB_PATH)


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)
