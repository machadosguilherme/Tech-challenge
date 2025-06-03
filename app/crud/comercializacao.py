# app/crud/comercializacao.py

import os
from typing import List, Optional

import pandas as pd
from fastapi import HTTPException
import requests

URL_COMERCIALIZACAO = "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_04"

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FALLBACK_CSV = os.path.join(ROOT, "data", "comercializacao.csv")


async def buscar_comercializacao(ano: Optional[int] = None) -> List[dict]:
    # TENTA LIVE
    try:
        head = requests.head(URL_COMERCIALIZACAO, timeout=5)
        head.raise_for_status()
        tables = pd.read_html(URL_COMERCIALIZACAO)
        df_live = tables[-1].copy()

        def clean_col(col: str) -> str:
            s = col.strip().lower()
            s = (
                s.replace("quantidade (l.)", "quantidade")
                 .replace("quantidade (l)", "quantidade")
                 .replace("quantidade(l.)", "quantidade")
                 .replace("quantidade(l)", "quantidade")
                 .replace("produto", "produto")
                 .replace("categoria", "categoria")
                 .replace("ano", "ano")
            )
            s = "".join(c if c.isalnum() or c == "_" else "_" for c in s)
            s = "_".join(s.split())
            return s

        df_live.columns = [clean_col(c) for c in df_live.columns]
        if "ano" not in df_live.columns:
            import urllib.parse as upp
            parsed = upp.urlparse(URL_COMERCIALIZACAO)
            query = upp.parse_qs(parsed.query)
            try:
                extracted = int(query.get("ano", [0])[0])
            except:
                extracted = 0
            df_live["ano"] = extracted

        obrig = {"ano", "categoria", "produto", "quantidade"}
        if not obrig.issubset(set(df_live.columns)):
            raise Exception("Colunas obrigatórias não encontradas no live.")

        df_live["quantidade"] = (
            df_live["quantidade"]
            .astype(str)
            .str.replace(r"[^\d\,\.]", "", regex=True)
            .str.replace(",", ".", regex=False)
            .str.replace(r"\.", "", regex=True)
            .replace("", "0")
            .astype(float)
        )

        if ano is not None:
            df_live = df_live[df_live["ano"] == ano]

        return df_live.to_dict(orient="records")

    except Exception:
        pass

    # ------------------------------------------------------------
    # Fallback-only CSV
    # ------------------------------------------------------------
    if not os.path.exists(FALLBACK_CSV):
        raise HTTPException(503, f"CSV de fallback não encontrado: {FALLBACK_CSV}")

    try:
        df_fb = pd.read_csv(FALLBACK_CSV)
    except Exception as e:
        raise HTTPException(500, f"Erro ao ler CSV de fallback: {e}")

    df_fb.rename(
        columns={
            "Ano": "ano",
            "Categoria": "categoria",
            "Produto": "produto",
            "Quantidade(L.)": "quantidade",
            "Quantidade(L)": "quantidade",
        },
        inplace=True,
        errors="ignore"
    )

    if "quantidade" in df_fb.columns:
        df_fb["quantidade"] = (
            df_fb["quantidade"]
            .astype(str)
            .str.replace(r"[^\d\,\.]", "", regex=True)
            .str.replace(",", ".", regex=False)
            .str.replace(r"\.", "", regex=True)
            .replace("", "0")
            .astype(float)
        )

    if "ano" in df_fb.columns:
        df_fb["ano"] = df_fb["ano"].astype(int)

    if ano is not None and "ano" in df_fb.columns:
        df_fb = df_fb[df_fb["ano"] == ano]

    obrig = {"ano", "categoria", "produto", "quantidade"}
    if not obrig.issubset(df_fb.columns):
        raise HTTPException(
            status_code=500,
            detail=f"Colunas obrigatórias faltando após mapeamento. Colunas atuais: {df_fb.columns.tolist()}"
        )

    return df_fb.to_dict(orient="records")
