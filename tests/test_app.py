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

def test_get_data_from_production_and_return_data_from_site():
    res = client.get("/production/")
    assert res.status_code == 200

    
    
    