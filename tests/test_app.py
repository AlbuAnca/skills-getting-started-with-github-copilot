import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

# Snapshot of initial state taken at import time
INITIAL_ACTIVITIES = copy.deepcopy(activities)

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore activities to their initial state before each test."""
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_all():
    # Arrange
    expected_count = len(INITIAL_ACTIVITIES)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert len(response.json()) == expected_count


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_new_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # already in initial data

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_signup_activity_not_found():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert "activity not found" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_unregister_existing_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # already in initial data

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]


def test_unregister_participant_not_signed_up():
    # Arrange
    activity_name = "Chess Club"
    email = "ghost@mergington.edu"  # not in this activity

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert "not signed up" in response.json()["detail"].lower()


def test_unregister_activity_not_found():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert "activity not found" in response.json()["detail"].lower()
