import uuid

import pytest


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("TESTING", "true")
    from swellbeing_api.app import create_app
    from swellbeing_api.database import db

    app = create_app(testing=True)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_user_lifecycle(client):
    assert client.get("/users").json == []

    response = client.post("/users")
    assert response.status_code == 201
    user = response.json
    assert uuid.UUID(user["id"]).version == 7
    path = f"/users/{user['id']}"

    assert client.get("/users").json == [user]
    assert client.get(path).json == user
    assert client.delete(path).status_code == 204
    assert client.get(path).status_code == 404
    assert client.delete(path).status_code == 204
    assert client.get("/users").json == []


def test_water_intake_creation(client):
    from swellbeing_api.database import db
    from swellbeing_api.models import WaterIntake

    user_id = client.post("/users").json["id"]
    response = client.post(f"/users/{user_id}/water_intakes", json={"volume": 250})
    assert response.status_code == 201
    with client.application.app_context():
        intake = db.session.get(WaterIntake, response.json["id"])
        assert intake.user_id == uuid.UUID(user_id)
        assert intake.volume == 250
    water_intake = response.json
    assert "timestamp" in water_intake
    assert water_intake["timestamp"] is not None
    response = client.get(f"/users/{user_id}/water_intakes")
    assert response.status_code == 200
    assert response.json == [water_intake]


def test_water_intake_requires_existing_user(client):
    response = client.post(f"/users/{uuid.uuid4()}/water_intakes", json={"volume": 250})
    assert response.status_code == 404


def test_water_intake_requires_volume(client):
    user_id = client.post("/users").json["id"]
    response = client.post(f"/users/{user_id}/water_intakes", json={})
    assert response.status_code == 400
    assert response.json == {"error": "Volume is required"}


def test_empty_water_intake_range(client):
    user_id = client.post("/users").json["id"]
    response = client.get(
        f"/users/{user_id}/water_intakes",
        query_string={"from": "2026-09-01T00:00:00", "to": "2026-10-01T00:00:00"},
    )
    assert response.status_code == 200
    assert response.json == []
