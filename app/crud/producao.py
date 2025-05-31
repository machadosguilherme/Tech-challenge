# app/crud/producao.py

import os
from typing import List, Optional

import pandas as pd
from fastapi import HTTPException
import requests

# URL para tentar live‐scraping
URL_PRODUCAO = "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_02"

# Caminho absoluto para o CSV de fallback
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FALLBACK_CSV = os.path.join(ROOT, "data", "producao.csv")


async def buscar_producao(ano: Optional[int] = None) -> List[dict]:
    """
    1) Tenta ler via pandas.read_html (live scraping).
    2) Se algo falhar, cai no CSV de fallback (data/producao.csv).
    3) Normaliza colunas para: ano (int), categoria (str), produto (str), quantidade (float).
    4) Filtra por ano (se fornecido) e devolve List[dict].
    """

    # ─── 1) TENTATIVA DE LIVE‐SCRAPING ─────────────────────────────────────────────
    try:
        # 1.1) Verifica rapidamente se o site está no ar (HEAD)
        resp_head = requests.head(URL_PRODUCAO, timeout=5)
        resp_head.raise_for_status()

        # 1.2) Lê todas as tabelas da página
        tables = pd.read_html(URL_PRODUCAO)
        df_live = tables[-1].copy()

        # 1.3) Normaliza o nome das colunas para canônico (lower, sem parênteses)
        def _clean_col(col: str) -> str:
            s = col.strip().lower()
            # Mapeamentos básicos (exemplo para “Quantidade (L.)” → “quantidade”)
            s = (
                s.replace("quantidade (l.)", "quantidade")
                 .replace("quantidade (l)", "quantidade")
                 .replace("quantidade(l.)", "quantidade")
                 .replace("quantidade(l)", "quantidade")
                 .replace("quantidade", "quantidade")
                 .replace("produto", "produto")
                 .replace("categoria", "categoria")
                 .replace("ano", "ano")
            )
            # Substitui símbolos não‐alfa‐numéricos por underline (_)
            s = "".join(c if c.isalnum() or c == "_" else "_" for c in s)
            s = "_".join(s.split())
            return s

        df_live.columns = [_clean_col(c) for c in df_live.columns]

        # 1.4) Se não houver coluna “ano” embutida, injetamos a partir do parametro “ano” da URL
        if "ano" not in df_live.columns:
            import urllib.parse as upp
            parsed = upp.urlparse(URL_PRODUCAO)
            query = upp.parse_qs(parsed.query)
            try:
                extracted = int(query.get("ano", [0])[0])
            except:
                extracted = 0
            df_live["ano"] = extracted

        # 1.5) Verifica se todas as colunas obrigatórias existem
        obrig = {"ano", "categoria", "produto", "quantidade"}
        if not obrig.issubset(set(df_live.columns)):
            raise Exception("Colunas obrigatórias faltando no live‐scraping")

        # 1.6) LIMPA formato de “quantidade” (remove pontos de milhares e converte para float)
        df_live["quantidade"] = (
            df_live["quantidade"]
            .astype(str)
            # 1) remove tudo o que não seja dígito, vírgula ou ponto
            .str.replace(r"[^\d\,\.]", "", regex=True)
            # 2) substitui vírgula decimal por ponto (se houver valores tipo "123,45")
            .str.replace(",", ".", regex=False)
            # 3) remove TODOS os pontos restantes (que são separadores de milhar)
            .str.replace(r"\.", "", regex=True)
            # 4) converte para float
            .replace("", "0")
            .astype(float)
        )

        # 1.7) Se veio “ano” na query-string, filtra
        if ano is not None:
            df_live = df_live[df_live["ano"] == ano]

        return df_live.to_dict(orient="records")

    except Exception:
        # Se qualquer erro ocorrer no bloco live, vamos ao fallback abaixo.
        pass


    # ─── 2) FALLBACK‐ONLY (CSV local) ────────────────────────────────────────────────
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

    # 2.1) Renomeia colunas para o padrão: ano, categoria, produto, quantidade
    df_fb.rename(
        columns={
            "Ano": "ano",
            "Categoria": "categoria",
            "Produto": "produto",
            "Quantidade(L.)": "quantidade",
            "Quantidade(L)": "quantidade",
            "Quantidade_L_": "quantidade",
        },
        inplace=True,
        errors="ignore"
    )

    # 2.2) Converte a coluna “quantidade” (que veio como "217.208.604" etc.) para float
    if "quantidade" in df_fb.columns:
        df_fb["quantidade"] = (
            df_fb["quantidade"]
            .astype(str)
            # 1) remove tudo o que não seja dígito, vírgula ou ponto
            .str.replace(r"[^\d\,\.]", "", regex=True)
            # 2) substitui vírgula decimal por ponto, se houver (ex.: "1.234,56")
            .str.replace(",", ".", regex=False)
            # 3) remove ponto de milhar
            .str.replace(r"\.", "", regex=True)
            .replace("", "0")
            .astype(float)
        )

    # 2.3) Converte “ano” para int
    if "ano" in df_fb.columns:
        df_fb["ano"] = df_fb["ano"].astype(int)

    # 2.4) Filtra por ano, se veio como parametro
    if ano is not None and "ano" in df_fb.columns:
        df_fb = df_fb[df_fb["ano"] == ano]

    # 2.5) Verifica novamente se todas as colunas obrigatórias estão lá
    obrig = {"ano", "categoria", "produto", "quantidade"}
    if not obrig.issubset(df_fb.columns):
        raise HTTPException(
            status_code=500,
            detail=f"Colunas obrigatórias faltando após mapeamento. Colunas atuais: {df_fb.columns.tolist()}"
        )

    return df_fb.to_dict(orient="records")
