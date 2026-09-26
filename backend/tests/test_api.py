from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def register(name, email, role="ATTENDEE"):
    return client.post("/api/register", json={"name": name, "email": email, "password": "password123", "role": role})

def auth(token):
    return {"Authorization": f"Bearer {token}"}

def test_health():
    assert client.get("/health").status_code == 200

def test_registration_and_duplicate():
    email = "test_unique@example.com"
    r = register("Test User", email)
    assert r.status_code in (201, 409)
    r2 = register("Test User", email)
    assert r2.status_code == 409

def test_organizer_event_and_attendee_rsvp():
    org = register("Org", "org_unique@example.com", "ORGANIZER")
    assert org.status_code in (201, 409)
    if org.status_code == 409:
        return
    org_token = org.json()["access_token"]
    e = client.post("/api/events", headers=auth(org_token), json={
        "event_name": "Test Workshop", "description": "test", "event_type": "Workshop",
        "event_date": "2099-01-01", "start_time": "10:00", "end_time": "12:00",
        "venue": "Virtual Lab", "maximum_capacity": 2, "registration_deadline": "2098-12-31"
    })
    assert e.status_code == 201
    event_id = e.json()["id"]
    attendee = register("Attendee", "attendee_unique@example.com")
    assert attendee.status_code == 201
    r = client.post(f"/api/events/{event_id}/rsvp", headers=auth(attendee.json()["access_token"]), json={"status":"GOING"})
    assert r.status_code == 200
