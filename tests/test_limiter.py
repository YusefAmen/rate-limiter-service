import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_rate_limit():
    for _ in range(5):
        r = client.get("/limited")
        assert r.status_code == 200
    r = client.get("/limited")
    assert r.status_code == 429
    assert r.json()["detail"] == "Rate limit exceeded" 