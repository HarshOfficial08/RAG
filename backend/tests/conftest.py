import pytest
from fastapi.testclient import TestClient
from qdrant_client import QdrantClient

from app.config import settings
from app.main import app

_TEST_COLLECTION = "documents_test"


@pytest.fixture(autouse=True, scope="session")
def _use_isolated_test_collection() -> None:
    # Tests that exercise the real ingestion pipeline write real vectors to
    # Qdrant — point them at a dedicated collection so test runs never mix
    # with (or pollute) whatever a developer is exploring against the same
    # Qdrant instance during manual testing.
    settings.qdrant_collection = _TEST_COLLECTION

    # Drop any leftovers from a previous run so each session starts from a
    # known-empty collection — otherwise accumulated fixture data from past
    # runs can pad out top-k search results and produce order-dependent flakes.
    client = QdrantClient(url=settings.qdrant_url)
    if client.collection_exists(_TEST_COLLECTION):
        client.delete_collection(_TEST_COLLECTION)


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)
