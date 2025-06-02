# tests/test_recurso.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# liste todos os seus recursos suportados
RECURSOS = [
    "producao",
    "processamento",
    "comercializacao",
    "importacao",
    "exportacao",
]

@pytest.mark.parametrize("recurso", RECURSOS)
def test_listar_tudo(recurso):
    """GET /{recurso}/ sem filtro deve devolver 200 e lista não vazia."""
    resp = client.get(f"/{recurso}/")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1, f"{recurso} retornou lista vazia"

@pytest.mark.parametrize("recurso", RECURSOS)
def test_filtrar_ano(recurso):
    """GET /{recurso}/?ano=1970 deve devolver apenas itens com ano 1970 (se coluna existir)."""
    resp = client.get(f"/{recurso}/?ano=1970")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    # Se o DataFrame não tiver coluna 'ano', retorna tudo sem filtrar:
    if data and "Ano" in data[0] or "ano" in data[0]:
        for item in data:
            # aceita tanto "ano" (live) quanto "Ano" (CSV)
            ano_val = item.get("ano") or item.get("Ano")
            assert ano_val == 1970
