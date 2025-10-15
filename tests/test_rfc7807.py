from app.utils.rfc7807 import problem


def test_problem_shape():
    resp = problem(404, "Not Found", "item missing")
    assert resp.status_code == 404
    data = resp.body.decode()
    for key in ("type", "title", "status", "detail", "correlation_id"):
        assert f'"{key}"' in data
