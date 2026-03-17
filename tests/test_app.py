import pytest
import app as app_module
from app import app as flask_app


@pytest.fixture(autouse=True)
def clear_employees():
    """Reset the in-memory dict before every test."""
    app_module.employees.clear()
    yield
    app_module.employees.clear()


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    return flask_app.test_client()


# ── Health ────────────────────────────────────────────────────────────────────

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"
    assert r.get_json()["employee_count"] == 0


# ── Add ───────────────────────────────────────────────────────────────────────

def test_add_json(client):
    r = client.post("/add", json={"id": 1, "name": "Subba", "salary": 70000})
    assert r.status_code == 201

def test_add_form(client):
    r = client.post("/add", data={"id": 2, "name": "Ravi", "salary": 50000})
    assert r.status_code == 201

def test_add_missing_fields(client):
    r = client.post("/add", json={"id": 1})
    assert r.status_code == 400

def test_add_duplicate(client):
    client.post("/add", json={"id": 1, "name": "Subba", "salary": 70000})
    r = client.post("/add", json={"id": 1, "name": "Subba", "salary": 70000})
    assert r.status_code == 409


# ── Get all ───────────────────────────────────────────────────────────────────

def test_get_all_empty(client):
    r = client.get("/all")
    assert r.status_code == 200
    assert r.get_json() == []

def test_get_all(client):
    client.post("/add", json={"id": 1, "name": "Subba", "salary": 70000})
    client.post("/add", json={"id": 2, "name": "Ravi",  "salary": 50000})
    r = client.get("/all")
    assert len(r.get_json()) == 2


# ── Get by ID ─────────────────────────────────────────────────────────────────

def test_get_by_id(client):
    client.post("/add", json={"id": 1, "name": "Subba", "salary": 70000})
    r = client.get("/byId/1")
    assert r.status_code == 200
    assert r.get_json()["name"] == "Subba"

def test_get_by_id_not_found(client):
    r = client.get("/byId/999")
    assert r.status_code == 404


# ── Get by name ───────────────────────────────────────────────────────────────

def test_get_by_name(client):
    client.post("/add", json={"id": 1, "name": "Anita", "salary": 60000})
    r = client.get("/byName/anita")          # case-insensitive
    assert r.status_code == 200
    assert r.get_json()["emp_id"] == 1

def test_get_by_name_not_found(client):
    r = client.get("/byName/Nobody")
    assert r.status_code == 404


# ── Update ────────────────────────────────────────────────────────────────────

def test_update(client):
    client.post("/add", json={"id": 1, "name": "Old", "salary": 30000})
    r = client.put("/update", json={"emp_id": 1, "name": "New", "salary": 40000})
    assert r.status_code == 200
    assert client.get("/byId/1").get_json()["name"] == "New"

def test_update_not_found(client):
    r = client.put("/update", json={"emp_id": 999, "name": "X"})
    assert r.status_code == 404

def test_update_non_json(client):
    r = client.put("/update", data={"emp_id": 1})
    assert r.status_code == 400


# ── Delete ────────────────────────────────────────────────────────────────────

def test_delete(client):
    client.post("/add", json={"id": 1, "name": "Subba", "salary": 70000})
    r = client.delete("/delete/1")
    assert r.status_code == 200
    assert client.get("/byId/1").status_code == 404

def test_delete_not_found(client):
    r = client.delete("/delete/999")
    assert r.status_code == 404

def test_delete_form(client):
    client.post("/add", json={"id": 2, "name": "Ravi", "salary": 50000})
    r = client.post("/delete", data={"delete_id": 2})
    assert r.status_code == 200

def test_delete_form_missing_id(client):
    r = client.post("/delete", data={})
    assert r.status_code == 400
