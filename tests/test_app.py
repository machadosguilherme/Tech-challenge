import json
import pytest
from app.main import app
import json
from fastapi.testclient import TestClient

client = TestClient(app)

def test_read_root():
    res = client.get("/")
    assert res.status_code == 200
    assert "Bem-vindo" in res.json()["message"]

def test_production_without_params():
    res = client.get("/production/")
    assert res.status_code == 200

def test_production_with_year():
    res = client.get("/production/?year=2023")
    assert res.status_code == 200

    
