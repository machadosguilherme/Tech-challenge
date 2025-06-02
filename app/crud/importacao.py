# app/crud/importacao.py

import os
from typing import List, Optional

import pandas as pd
from fastapi import HTTPException
import requests

URL_IMPORTACAO = "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_05"

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FALLBACK_CSV = os.path.join(ROOT, "data", "importacao.csv")


async def buscar_importacao(ano: Optional[int] = None) -> List[dict]:
    """
    1) Tenta live‐scraping com pd.read_html.
    2) Se falhar, usa data/importacao.csv.
    3) Renomeia:
        "Opção" -> "opcao"
        "Ano"   -> "ano"
        "Países"-> "paises"
        "Quantidade (Kg.)" -> "quantidade"
        "Valor (US$)" -> "valor_us"
    4) Converte quantidade e valor_us para float (removendo ponto de milhar).
    5) Filtra por ano.
    """

    # ─── 1) LIVE‐SCRAPING ───────────────────────────────────────────────────────────
    try:
        resp_head = requests.head(URL_IMPORTACAO, timeout=5)
        resp_head.raise_for_status()

        tables = pd.read_html(URL_IMPORTACAO)
        df_live = tables[-1].copy()

        def _clean_col(c: str) -> str:
            s = c.strip().lower()
            if "opção" in s:
                return "opcao"
            if s == "ano":
                return "ano"
            if "país" in s:
                return "paises"
            if "quantidade" in s and "kg" in s:
                return "quantidade"
            if "valor" in s and "us" in s:
                return "valor_us"
            s = "".join(ch if ch.isalnum() else "_" for ch in s)
            s = "_".join(s.split())
            return s

        df_live.columns = [_clean_col(c) for c in df_live.columns]

        if "ano" not in df_live.columns:
            import urllib.parse as upp
            parsed = upp.urlparse(URL_IMPORTACAO)
            query = upp.parse_qs(parsed.query)
            try:
                extracted = int(query.get("ano", [0])[0])
            except:
                extracted = 0
            df_live["ano"] = extracted

        obrig = {"opcao", "ano", "paises", "quantidade", "valor_us"}
        if not obrig.issubset(set(df_live.columns)):
            raise Exception(f"Colunas faltando no live: {df_live.columns.tolist()}")

        df_live["quantidade"] = (
            df_live["quantidade"]
            .astype(str)
            .str.replace(r"[^\d\,\.]", "", regex=True)
            .str.replace(",", ".", regex=False)
            .str.replace(r"\.", "", regex=True)
            .replace("", "0")
            .astype(float)
        )
        df_live["valor_us"] = (
            df_live["valor_us"]
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


    # ─── 2) FALLBACK ─────────────────────────────────────────────────────────────────
    if not os.path.exists(FALLBACK_CSV):
        raise HTTPException(
            status_code=503,
            detail=f"CSV de fallback não encontrado em: {FALLBACK_CSV}"
        )

    try:
        df_fb = pd.read_csv(FALLBACK_CSV)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao ler o CSV de fallback: {e}"
        )

    df_fb.rename(
        columns={
            "Opção": "opcao",
            "Ano": "ano",
            "Países": "paises",
            "Quantidade (Kg.)": "quantidade",
            "Quantidade(Kg.)": "quantidade",
            "Valor (US$)": "valor_us",
            "Valor(US$)": "valor_us",
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
    if "valor_us" in df_fb.columns:
        df_fb["valor_us"] = (
            df_fb["valor_us"]
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

    obrig = {"opcao", "ano", "paises", "quantidade", "valor_us"}
    if not obrig.issubset(set(df_fb.columns)):
        raise HTTPException(
            status_code=500,
            detail=f"Colunas obrigatórias faltando após mapeamento. Colunas atuais: {df_fb.columns.tolist()}"
        )

    return df_fb.to_dict(orient="records")
