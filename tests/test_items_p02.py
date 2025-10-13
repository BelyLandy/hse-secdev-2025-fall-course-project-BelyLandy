from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_filter_by_label():
    h = {"X-User-Id": "u_lbl"}
    client.post(
        "/api/v1/items",
        headers=h,
        json={"title": "ux-1", "impact": 5, "effort": 5, "labels": ["ux"]},
    )
    client.post(
        "/api/v1/items",
        headers=h,
        json={"title": "be-1", "impact": 5, "effort": 5, "labels": ["backend"]},
    )

    r = client.get("/api/v1/items?label=ux", headers=h)
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 1
    assert all("ux" in it["labels"] for it in data)


def test_admin_list_sees_all():
    id1 = client.post(
        "/api/v1/items",
        headers={"X-User-Id": "p02_a"},
        json={"title": "A", "impact": 3, "effort": 3},
    ).json()["id"]
    id2 = client.post(
        "/api/v1/items",
        headers={"X-User-Id": "p02_b"},
        json={"title": "B", "impact": 3, "effort": 3},
    ).json()["id"]

    r = client.get(
        "/api/v1/items?limit=100",
        headers={"X-User-Id": "admin", "X-User-Role": "admin"},
    )
    assert r.status_code == 200
    ids = {it["id"] for it in r.json()}
    assert {id1, id2}.issubset(ids)
