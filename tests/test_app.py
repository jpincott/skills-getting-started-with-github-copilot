from copy import deepcopy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    baseline = deepcopy(activities)
    yield
    activities.clear()
    activities.update(baseline)

def test_root_redirect():
    resp = client.get("/")
    assert resp.status_code in (302, 307)
    assert resp.headers["location"] == "/static/index.html"

def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert "Chess Club" in resp.json()

def test_signup_success():
    email = "newstudent@mergington.edu"
    resp = client.post("/activities/Chess Club/signup", params={"email": email})
    assert resp.status_code == 200
    assert resp.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]

def test_signup_duplicate():
    email = "michael@mergington.edu"
    resp = client.post("/activities/Chess Club/signup", params={"email": email})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Student is already signed up for this activity"

def test_signup_activity_not_found():
    resp = client.post("/activities/NoActivity/signup", params={"email": "x@y.com"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Activity not found"

def test_remove_participant_success():
    email = "alex@mergington.edu"
    resp = client.delete("/activities/Basketball Team/participants", params={"email": email})
    assert resp.status_code == 200
    assert resp.json() == {"message": f"Removed {email} from Basketball Team"}
    assert email not in activities["Basketball Team"]["participants"]

def test_remove_participant_not_found():
    resp = client.delete("/activities/Gym Class/participants", params={"email": "doesnotexist@mergington.edu"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Participant not found"

def test_remove_activity_not_found():
    resp = client.delete("/activities/NoActivity/participants", params={"email": "x@y.com"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Activity not found"
