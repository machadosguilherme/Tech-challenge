# dashboard/app.py

import streamlit as st
import pandas as pd
import requests
import re
import unicodedata
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# ─── Configuração da página ─────────────────────────────────────────────────────
st.set_page_config(page_title="Dashboard Vinicultura", layout="wide")

# ─── Sidebar: autenticação ───────────────────────────────────────────────────────
st.sidebar.header("🔐 Autenticação")
if "token" not in st.session_state:
    user = st.sidebar.text_input("Usuário")
    pwd  = st.sidebar.text_input("Senha", type="password")
    if st.sidebar.button("Login"):
        r = requests.post(
            f"{API_URL}/token",
            data={"username": user, "password": pwd},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if r.status_code == 200:
            st.session_state.token = r.json()["access_token"]
            st.sidebar.success("Autenticado!")
        else:
            st.sidebar.error("Login falhou. Verifique credenciais.")
            st.stop()
    else:
        st.title("🔐 Faça login para acessar o dashboard")
        st.stop()
else:
    st.sidebar.success("✅ Você está autenticado")

# ─── Título ──────────────────────────────────────────────────────────────────────
st.title("📊 Dashboard de Vitivinicultura")

# ─── Seletores ───────────────────────────────────────────────────────────────────
recurso = st.sidebar.selectbox(
    "Recurso",
    ["producao", "processamento", "comercializacao", "importacao", "exportacao"]
)
ano_min = st.sidebar.slider("Ano mínimo", 1970, 2023, 1970)

# ─── Chamada à API ───────────────────────────────────────────────────────────────
headers = {"Authorization": f"Bearer {st.session_state.token}"}
resp = requests.get(
    f"{API_URL}/{recurso}/",
    params={"ano": ano_min},
    headers=headers
)
try:
    resp.raise_for_status()
except requests.HTTPError as e:
    st.error(f"Erro {e.response.status_code}: {e.response.text}")
    st.stop()

# ─── Extração de JSON ─────────────────────────────────────────────────────────────
json_obj = resp.json()

# Detectamos se a resposta veio no formato {"source": "...", "data": [...]} ou se é só lista:
if isinstance(json_obj, dict) and ("data" in json_obj):
    source    = json_obj.get("source", None)
    registros = json_obj.get("data", [])
else:
    source    = None
    registros = json_obj  # supõe-se que seja lista de dicionários

# ─── Construção do DataFrame a partir de 'registros' ─────────────────────────────
df = pd.DataFrame(registros)

# Se não houver nenhum registro, avisamos e encerramos a exibição
if df.empty:
    st.warning("Nenhum registro retornado para este filtro.")
else:
    # Se tivermos uma fonte (wrapper), mostramos
    if source:
        st.info(f"✅ Fonte de dados: **{source}**")

    # ─── DEBUG: Colunas originais antes de ajustar ────────────────────────────────
    st.write("**Colunas originais:**", df.columns.tolist())

    # ─── Função de limpeza de nome de coluna ───────────────────────────────────────
    def clean_col(name: str) -> str:
        # Remove acentos
        nfkd = unicodedata.normalize("NFKD", str(name))
        no_accent = "".join(c for c in nfkd if not unicodedata.combining(c))
        # lowercase + replace não-word por "_"
        s = no_accent.lower()
        s = re.sub(r"\W+", "_", s)
        return s.strip("_")

    df.columns = [clean_col(c) for c in df.columns]
    st.write("**Colunas após clean:**", df.columns.tolist())

    # ─── Padroniza coluna "quantidade" ────────────────────────────────────────────
    qty_cols = [c for c in df.columns if "quantidade" in c]
    if qty_cols:
        df = df.rename(columns={qty_cols[0]: "quantidade"})

    # ─── Padroniza coluna "paises" ────────────────────────────────────────────────
    pais_cols = [c for c in df.columns if "pais" in c]
    if pais_cols:
        df = df.rename(columns={pais_cols[0]: "paises"})

    st.write("**Colunas finais:**", df.columns.tolist())

    # ─── Exibição da tabela ────────────────────────────────────────────────────────
    st.subheader(f"{recurso.capitalize()} — {len(df)} registros")
    st.dataframe(df, use_container_width=True)

    # ─── Botão de download ─────────────────────────────────────────────────────────
    st.download_button(
        "🔽 Baixar CSV",
        df.to_csv(index=False),
        f"{recurso}.csv",
        "text/csv"
    )

    # ─── Gráfico de série temporal ────────────────────────────────────────────────
    if {"ano", "quantidade"}.issubset(df.columns):
        df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce").fillna(0)
        series = df.groupby("ano")["quantidade"].sum()
        st.subheader("🔢 Série temporal de Quantidade")
        st.line_chart(series)
    else:
        faltam = [c for c in ("ano", "quantidade") if c not in df.columns]
        st.info(f"Gráfico de série desativado, faltando coluna(s): {faltam}")

    # ─── Bar chart top‐10 países ───────────────────────────────────────────────────
    if {"paises", "quantidade"}.issubset(df.columns):
        st.subheader(f"📊 Top 10 países por Quantidade em {ano_min}")
        top10 = (
            df.groupby("paises")["quantidade"]
              .sum()
              .sort_values(ascending=False)
              .head(10)
        )
        st.bar_chart(top10)
    else:
        faltam = [c for c in ("paises", "quantidade") if c not in df.columns]
        st.info(f"Bar chart desativado, faltando coluna(s): {faltam}")
