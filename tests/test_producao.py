from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_listar_tudo():
    response = client.get("/producao/")
    assert response.status_code == 200
    data = response.json()
    # deve ser uma lista e conter pelo menos uma entrada
    assert isinstance(data, list)
    assert len(data) >= 1

def test_filtrar_ano():
    response = client.get("/producao/?ano=2022")
    assert response.status_code == 200
    data = response.json()
    # cada item deve ter o campo ano == 2022
    assert all(item["ano"] == 2022 for item in data)
