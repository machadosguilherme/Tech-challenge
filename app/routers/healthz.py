# app/routers/healthz.py

import os
import pandas as pd
import urllib.request
from fastapi import APIRouter, HTTPException

router = APIRouter()

# 5 URLs “ao vivo” (Embrapa)
URLS_LIVE = {
    "producao":       "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_02",
    "processamento":  "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_03",
    "comercializacao":"http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_04",
    "importacao":     "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_05",
    "exportacao":     "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_06",
}

# caminhos absolutos para os 5 CSVs de fallback
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CSVS_FALLBACK = {
    "producao":       os.path.join(ROOT, "data", "producao.csv"),
    "processamento":  os.path.join(ROOT, "data", "processamento.csv"),
    "comercializacao":os.path.join(ROOT, "data", "comercializacao.csv"),
    "importacao":     os.path.join(ROOT, "data", "importacao.csv"),
    "exportacao":     os.path.join(ROOT, "data", "exportacao.csv"),
}


@router.get("/", summary="Health check detalhado")
async def healthz():
    """
    Retorna {"status":"ok", "detalhe": {...}}. Em 'detalhe' verificamos:
      • se cada CSV de fallback existe (checa o arquivo em disco)
      • se cada URL "ao vivo" responde com HTTP HEAD
    """

    detalhe = {}

    # 1) Verifica existência de cada CSV de fallback
    csv_status = {}
    for key, path_csv in CSVS_FALLBACK.items():
        if os.path.exists(path_csv):
            csv_status[f"csv_{key}"] = "existe"
        else:
            csv_status[f"csv_{key}"] = "falta"

    # 2) Faz um HEAD rápido em cada URL. Se der erro (404, timeout, etc.), marca "falha".
    live_status = {}
    for key, url in URLS_LIVE.items():
        try:
            # Apenas a requisição HEAD, sem baixar todo o HTML
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    live_status[f"live_{key}"] = "ok"
                else:
                    live_status[f"live_{key}"] = f"HTTP {resp.status}"
        except Exception as e:
            live_status[f"live_{key}"] = f"falha ({type(e).__name__})"

    # 3) Monta o dicionário “detalhe” unindo os dois status
    detalhe.update(live_status)
    detalhe.update(csv_status)

    return {"status": "ok", "detalhe": detalhe}
