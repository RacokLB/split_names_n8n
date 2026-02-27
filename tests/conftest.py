import pytest
import os

# Set env vars before importing the app (main.py validates at import time)
os.environ["TESTING"] = "1"
os.environ["API_KEY"] = "test-secret-key-for-testing-only"

from fastapi.testclient import TestClient
from main import app

TEST_API_KEY = "test-secret-key-for-testing-only"


@pytest.fixture
def client():
    """Provides a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Provides valid authentication headers."""
    return {"X-API-Key": TEST_API_KEY}
