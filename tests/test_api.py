import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

@pytest.fixture(scope="module")
def film_data():
    payload = {"titre": "TestFilm", "description": "Desc", "age_min": 0}
    r = client.post("/films", json=payload)
    assert r.status_code == 201
    return r.json()

def test_list_films(film_data):
    r = client.get("/films")
    assert r.status_code == 200
    titres = [f["titre"] for f in r.json()]
    assert "TestFilm" in titres

@pytest.fixture(scope="module")
def user_data():
    payload = {
        "email": "u1@example.com",
        "password": "Pwd123$$",
        "first_name": "Jean",
        "last_name": "Dupont"
    }
    r = client.post("/users", json=payload)
    assert r.status_code == 201
    return r.json()

def test_login(user_data):
    payload = {"email": user_data["email"], "password": "Pwd123$$"}
    r = client.post("/login", json=payload)
    assert r.status_code == 200
    assert r.json()["message"] == "Connexion réussie"

@pytest.fixture(scope="module")
def seance_data(film_data):
    payload = {
        "film_id": film_data["id"],
        "cinema_id": 1,
        "date": "2025-07-10",
        "heure_debut": "20:00:00",
        "heure_fin": "22:00:00",
        "salle": "1",
        "qualite": "4K",
        "places_totales": 50,
        "places_dispo": 50
    }
    r = client.post("/seances", json=payload)
    assert r.status_code == 201
    return r.json()

def test_list_seances(seance_data):
    r = client.get("/seances")
    assert r.status_code == 200
    ids = [s["id"] for s in r.json()]
    assert seance_data["id"] in ids

@pytest.fixture(scope="module")
def reservation_data(user_data, seance_data):
    payload = {
        "user_id": user_data["id"],
        "seance_id": seance_data["id"],
        "nb_places": 2,
        "sieges": "A1,A2"
    }
    r = client.post("/reservations", json=payload)
    assert r.status_code == 201
    return r.json()

def test_user_reservations(user_data, reservation_data):
    r = client.get(f'/users/{user_data["id"]}/reservations')
    assert r.status_code == 200
    assert any(res["id"] == reservation_data["id"] for res in r.json())
