from fastapi.testclient import TestClient

from src.app import app, activities


def test_unregister_participant_from_activity():
    client = TestClient(app)
    original_participants = list(activities["Chess Club"]["participants"])

    try:
        response = client.delete(
            "/activities/Chess%20Club/signup",
            params={"email": "michael@mergington.edu"},
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    finally:
        activities["Chess Club"]["participants"] = original_participants


def test_activities_endpoint_is_not_cached():
    client = TestClient(app)

    response = client.get("/activities")

    assert response.status_code == 200
    assert "no-store" in response.headers.get("cache-control", "").lower()
