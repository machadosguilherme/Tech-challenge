# app/crud/processamento.py

import os
from typing import List, Optional

import pandas as pd
from fastapi import HTTPException

# 1) URL “ao vivo” para scraping (poderá falhar, então temos fallback)
URL_PROCESSAMENTO = "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_03"

# 2) Caminho absoluto para o CSV de fallback
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FALLBACK_CSV = os.path.join(ROOT, "data", "processamento.csv")


async def buscar_processamento(ano: Optional[int] = None) -> List[dict]:
    """
    Retorna os dados de Processamento:
      1) Tenta scraping “ao vivo” via pd.read_html(URL_PROCESSAMENTO).
         - Percorre cada DataFrame retornado por read_html
           até encontrar aquele que tenha coluna “Ano” ou “Opção”.
      2) Se perceber que nenhuma tabela é válida (ou der erro), carrega o CSV de fallback.
      3) Normaliza nomes de coluna e converte “quantidade” para numérico.
      4) Filtra por ‘ano’, se for passado.
      5) Retorna a lista de dicionários prontos para JSON.
    """

    # ─── 1) TENTAR SCRAPING AO VIVO ─────────────────────────────────────────────────
    try:
        all_tables = pd.read_html(URL_PROCESSAMENTO, decimal=",", thousands=".")
        # Percorremos todas as tabelas lidas para encontrar a que tem “Ano” na coluna.
        df_live = None
        for df_candidate in all_tables:
            # Muitas vezes a “tabela de apresentação” vem como algo sem colunas nomeadas.
            # Então, testamos se existe “Ano” ou “Opção” em df_candidate.columns
            cols = [str(c).strip() for c in df_candidate.columns]
            if "Ano" in cols or "Opção" in cols:
                df_live = df_candidate.copy()
                break

        if df_live is None:
            # Não encontramos nenhuma tabela com “Ano” ou “Opção”
            raise ValueError("Nenhuma tabela válida encontrada no HTML de live scraping.")

        # Normalizar cabeçalhos do DataFrame vivo:
        df_live.columns = [str(c).strip() for c in df_live.columns]

        # Fazer o mapeamento exato das colunas que interessam:
        # Colunas esperadas no site:
        #   ["Opção", "Ano", "Categoria", "Cultivar", "Quantidade(Kg.)"]
        # Vamos renomear tudo para lower-case sem acentos, conforme nosso modelo:
        df_live = df_live.rename(
            columns={
                "Opção": "opcao",
                "Ano": "ano",
                "Categoria": "categoria",
                "Cultivar": "produto",           # usamos "produto" para corresponder ao schema
                "Quantidade(Kg.)": "quantidade",  # renomeia para "quantidade"
            }
        )

        # Descartar a coluna “opcao” (não faz parte do JSON final)
        if "opcao" in df_live.columns:
            df_live = df_live.drop(columns=["opcao"])

        # Converter “ano” para inteiro, se existir
        if "ano" in df_live.columns:
            df_live["ano"] = df_live["ano"].astype(int, errors="ignore")

        # Converter “quantidade” para float:
        if "quantidade" in df_live.columns:
            # Primeiro, transformar tudo em string para podermos remover pontos e trocar vírgula por ponto
            df_live["quantidade"] = (
                df_live["quantidade"]
                .astype(str)
                .str.replace(r"\.", "", regex=True)  # remove pontos de milhar
                .str.replace(",", ".", regex=False)   # vírgula decimal → ponto
            )
            df_live["quantidade"] = pd.to_numeric(df_live["quantidade"], errors="coerce").fillna(0)

        # Filtrar por “ano”, se tiver sido passado
        if ano is not None and "ano" in df_live.columns:
            df_live = df_live[df_live["ano"] == ano]

        # Pronto: devolve os registros encontrados “ao vivo”
        return df_live.to_dict(orient="records")

    except Exception as exc_live:
        # Qualquer erro (conexão, parse, sem tabela válida…) faz cair aqui.
        print("→ [PROCESSAMENTO] Falha no LIVE scraping:", exc_live)
        print("→ [PROCESSAMENTO] Usando CSV de fallback:", FALLBACK_CSV)

    # ─── 2) SE CHEGAR AQUI, NÃO FOI POSSÍVEL PEGAR AO VIVO → USA O CSV ───────────────
    if not os.path.exists(FALLBACK_CSV):
        raise HTTPException(
            status_code=503,
            detail=f"CSV de fallback não encontrado em: {FALLBACK_CSV}"
        )

    try:
        df_fb = pd.read_csv(FALLBACK_CSV)
    except Exception as exc_csv:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao ler CSV de fallback: {exc_csv}"
        )

    # ─── 3) NORMALIZAR COLUNAS DO CSV DE FALLBACK ────────────────────────────────────
    # No seu CSV, as colunas vieram assim: ['opcao', 'Ano', 'Categoria', 'produto', 'quantidade']
    # Vamos padronizar tudo para minúsculas + sem espaços, renomear “Ano”→“ano”, etc.

    # 3.1: strip/limpar bordas e forçar lower-case
    df_fb.columns = [str(c).strip() for c in df_fb.columns]

    # 3.2: renomear conforme padrão desejado
    mapping = {}
    for col in df_fb.columns:
        low = col.lower()
        if low == "ano":
            mapping[col] = "ano"
        elif low == "categoria":
            mapping[col] = "categoria"
        elif low in ("cultivar", "produto"):
            # Se a coluna vier “produto” ou “cultivar”, mapeamos para “produto”
            mapping[col] = "produto"
        elif "quantidade" in low:
            # Se a coluna contiver “quantidade” (por exemplo, “quantidade” ou “quantidade(kg.)”),
            # mapeamos para “quantidade”
            mapping[col] = "quantidade"
        else:
            # Por exemplo “opcao”: marcamos como “opcao” também (mas depois vamos descartar)
            mapping[col] = low

    df_fb = df_fb.rename(columns=mapping)

    # 3.3: descartar “opcao”
    if "opcao" in df_fb.columns:
        df_fb = df_fb.drop(columns=["opcao"])

    # 3.4: converter “ano” para int
    if "ano" in df_fb.columns:
        df_fb["ano"] = df_fb["ano"].astype(int, errors="ignore")

    # 3.5: converter “quantidade” para float
    if "quantidade" in df_fb.columns:
        df_fb["quantidade"] = (
            df_fb["quantidade"]
            .astype(str)
            .str.replace(r"\.", "", regex=True)  # remove pontos de milhar
            .str.replace(",", ".", regex=False)   # vírgula decimal → ponto
        )
        df_fb["quantidade"] = pd.to_numeric(df_fb["quantidade"], errors="coerce").fillna(0)

    # ─── 4) FILTRAR POR ANO (SE PASSADO) ─────────────────────────────────────────────
    if ano is not None and "ano" in df_fb.columns:
        df_fb = df_fb[df_fb["ano"] == ano]

    # ─── 5) RETORNAR LISTA DE DICIONÁRIOS ────────────────────────────────────────────
    return df_fb.to_dict(orient="records")
