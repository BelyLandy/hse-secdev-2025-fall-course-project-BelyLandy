from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
HEADERS = {"X-User-Id": "u1"}


def test_crud_happy_path():
    payload = {"title": "Idea A", "impact": 8, "effort": 2, "labels": ["ux", "quick"]}
    r = client.post("/api/v1/items", headers=HEADERS, json=payload)
    assert r.status_code == 201
    created = r.json()
    item_id = created["id"]
    assert created["owner_id"] == "u1"
    assert created["score"] == 4.0

    r = client.get(f"/api/v1/items/{item_id}", headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["title"] == "Idea A"

    r = client.get("/api/v1/items?sort=-score", headers=HEADERS)
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    r = client.patch(f"/api/v1/items/{item_id}", headers=HEADERS, json={"effort": 4})
    assert r.status_code == 200
    assert r.json()["score"] == 2.0

    r = client.delete(f"/api/v1/items/{item_id}", headers=HEADERS)
    assert r.status_code == 204


def test_owner_only_access():
    r = client.post(
        "/api/v1/items",
        headers={"X-User-Id": "u1"},
        json={"title": "X", "impact": 5, "effort": 5},
    )
    item_id = r.json()["id"]

    r = client.get(f"/api/v1/items/{item_id}", headers={"X-User-Id": "u2"})
    assert r.status_code == 403

    r = client.get(
        f"/api/v1/items/{item_id}",
        headers={"X-User-Id": "admin", "X-User-Role": "admin"},
    )
    assert r.status_code == 200


def test_validation_bad_labels():
    bad = {"title": "A", "impact": 5, "effort": 5, "labels": ["x" * 25]}
    r = client.post("/api/v1/items", headers=HEADERS, json=bad)
    assert r.status_code == 422
