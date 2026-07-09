import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture()
def client():
    # Arrange
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def restore_activities_state():
    # Arrange
    original_state = copy.deepcopy(activities)

    yield

    # Cleanup
    activities.clear()
    activities.update(copy.deepcopy(original_state))


def test_get_activities_returns_activity_data_and_no_store_header(client):
    # Arrange
    endpoint = "/activities"

    # Act
    response = client.get(endpoint)

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert response.headers["cache-control"].lower() == "no-store"


def test_signup_for_activity_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name.replace(' ', '%20')}/signup",
        params={"email": new_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
    assert new_email in activities[activity_name]["participants"]


def test_signup_for_activity_rejects_duplicate_registration(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name.replace(' ', '%20')}/signup",
        params={"email": existing_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities[activity_name]["participants"].count(existing_email) == 1


def test_unregister_from_activity_removes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name.replace(' ', '%20')}/signup",
        params={"email": existing_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {existing_email} from {activity_name}"
    assert existing_email not in activities[activity_name]["participants"]


def test_unregister_from_activity_rejects_missing_participant(client):
    # Arrange
    activity_name = "Chess Club"
    missing_email = "missing@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name.replace(' ', '%20')}/signup",
        params={"email": missing_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_root_redirects_to_static_index(client):
    # Arrange
    root_endpoint = "/"

    # Act
    response = client.get(root_endpoint, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"
