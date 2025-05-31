# app/crud/exportacao.py

import os
from typing import List, Optional

import pandas as pd
from fastapi import HTTPException
import requests

# 1) URL para tentar live‐scraping (se desejar reativar)
URL_EXPORTACAO = "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_06"

# 2) Caminho absoluto para o CSV de fallback (data/exportacao.csv)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FALLBACK_CSV = os.path.join(ROOT, "data", "exportacao.csv")


async def buscar_exportacao(ano: Optional[int] = None) -> List[dict]:
    """
    Tenta ler live (pd.read_html). Se falhar, cai no CSV de fallback.
    Renomeia colunas:
        "Opção"        -> "opcao"
        "Ano"          -> "ano"
        "Países"       -> "paises"
        "Quantidade(Kg.)" -> "quantidade"
        "Valor (US$)"  -> "valor_us"
    Converte 'quantidade' e 'valor_us' de string com ponto de milhar para float.
    Filtra por ano (se fornecido).
    """

    # ─── 1) TENTATIVA DE LIVE‐SCRAPING ─────────────────────────────────────────────
    try:
        resp_head = requests.head(URL_EXPORTACAO, timeout=5)
        resp_head.raise_for_status()

        tables = pd.read_html(URL_EXPORTACAO)
        df_live = tables[-1].copy()

        # Normaliza nome das colunas
        def _clean_col(col: str) -> str:
            s = col.strip().lower()
            # Ajustes pontuais para cada cabeçalho:
            if "opção" in s:
                return "opcao"
            if s == "ano":
                return "ano"
            if "país" in s:
                return "paises"
            if "quantidade" in s and "kg" in s.lower():
                return "quantidade"
            if "valor" in s and "us" in s.lower():
                return "valor_us"
            # Caso tenha algum caractere estranho, usa underline:
            s = "".join(c if c.isalnum() else "_" for c in s)
            s = "_".join(s.split())
            return s

        df_live.columns = [_clean_col(c) for c in df_live.columns]

        # Se não vier a coluna “ano” (por algum motivo), podemos extrair do query-string:
        if "ano" not in df_live.columns:
            import urllib.parse as upp
            parsed = upp.urlparse(URL_EXPORTACAO)
            query = upp.parse_qs(parsed.query)
            try:
                extracted = int(query.get("ano", [0])[0])
            except:
                extracted = 0
            df_live["ano"] = extracted

        # Verifica se todas as colunas obrigatórias existem
        obrig = {"opcao", "ano", "paises", "quantidade", "valor_us"}
        if not obrig.issubset(set(df_live.columns)):
            raise Exception(f"Colunas faltando no live: {df_live.columns.tolist()}")

        # Converte quantidade (remove ponto de milhar, vírgula decimal etc.)
        df_live["quantidade"] = (
            df_live["quantidade"]
            .astype(str)
            .str.replace(r"[^\d\,\.]", "", regex=True)
            .str.replace(",", ".", regex=False)
            .str.replace(r"\.", "", regex=True)
            .replace("", "0")
            .astype(float)
        )
        # Converte valor_us (mesma lógica)
        df_live["valor_us"] = (
            df_live["valor_us"]
            .astype(str)
            .str.replace(r"[^\d\,\.]", "", regex=True)
            .str.replace(",", ".", regex=False)
            .str.replace(r"\.", "", regex=True)
            .replace("", "0")
            .astype(float)
        )

        # Filtra por ano
        if ano is not None:
            df_live = df_live[df_live["ano"] == ano]

        return df_live.to_dict(orient="records")

    except Exception:
        # Se qualquer falha no scraping, cai no fallback:
        pass


    # ─── 2) FALLBACK (CSV local) ───────────────────────────────────────────────────
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

    # Renomeia colunas do CSV:
    df_fb.rename(
        columns={
            "Opção": "opcao",
            "Ano": "ano",
            "Países": "paises",
            "Quantidade(Kg.)": "quantidade",
            "Quantidade (Kg.)": "quantidade",
            "Valor (US$)": "valor_us",
            "Valor(US$)": "valor_us",
        },
        inplace=True,
        errors="ignore"
    )

    # Converte tipos:
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

    # Filtra por ano
    if ano is not None and "ano" in df_fb.columns:
        df_fb = df_fb[df_fb["ano"] == ano]

    # Verifica colunas obrigatórias após rename
    obrig = {"opcao", "ano", "paises", "quantidade", "valor_us"}
    if not obrig.issubset(set(df_fb.columns)):
        raise HTTPException(
            status_code=500,
            detail=f"Colunas obrigatórias faltando após mapeamento. Colunas atuais: {df_fb.columns.tolist()}"
        )

    return df_fb.to_dict(orient="records")
