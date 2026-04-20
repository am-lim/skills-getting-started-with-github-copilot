import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Snapshot and restore activities state between tests."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


client = TestClient(app)


def test_root_redirects_to_index():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    for name, details in data.items():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details


def test_signup_success():
    response = client.post(
        "/activities/Chess Club/signup?email=newstudent@mergington.edu"
    )
    assert response.status_code == 200
    assert "newstudent@mergington.edu" in response.json()["message"]
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_activity_not_found():
    response = client.post(
        "/activities/Nonexistent Club/signup?email=test@mergington.edu"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_email():
    response = client.post(
        "/activities/Chess Club/signup?email=michael@mergington.edu"
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_unregister_success():
    response = client.delete(
        "/activities/Chess Club/signup?email=michael@mergington.edu"
    )
    assert response.status_code == 200
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_activity_not_found():
    response = client.delete(
        "/activities/Nonexistent Club/signup?email=test@mergington.edu"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_email_not_signed_up():
    response = client.delete(
        "/activities/Chess Club/signup?email=nobody@mergington.edu"
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"
