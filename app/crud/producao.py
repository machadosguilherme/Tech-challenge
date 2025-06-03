# app/crud/producao.py

import os
from typing import List, Optional

import pandas as pd
from fastapi import HTTPException
import requests
import asyncio
import datetime
from bs4 import BeautifulSoup
import io


# URL para tentar live‐scraping
URL_PRODUCAO = "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_02"

# Caminho absoluto para o CSV de fallback
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FALLBACK_CSV = os.path.join(ROOT, "data", "producao.csv")

def extrair_categoria(control):
    # Categorias principais (linhas que não começam com prefixo)
    if not any(control.startswith(prefix) for prefix in ['vm_', 'vv_', 'su_', 'de_']):
        return control
    # Subcategorias de VINHO DE MESA
    elif control.startswith('vm_'):
        return 'VINHO DE MESA'
    # Subcategorias de VINHO FINO (VINIFERA)
    elif control.startswith('vv_'):
        return 'VINHO FINO DE MESA (VINIFERA)'
    # Subcategorias de SUCO
    elif control.startswith('su_'):
        return 'SUCO'
    # Subcategorias de DERIVADOS
    elif control.startswith('de_'):
        return 'DERIVADOS'
    else:
        return '-'

async def buscar_producao(ano: Optional[int] = None) -> List[dict]:
    """
    1) Tenta ler via pandas.read_html (live scraping).
    2) Se algo falhar, cai no CSV de fallback (data/producao.csv).
    3) Normaliza colunas para: ano (int), categoria (str), produto (str), quantidade (float).
    4) Filtra por ano (se fornecido) e devolve List[dict].
    """

    # ─── 1) TENTATIVA DE LIVE‐SCRAPING ─────────────────────────────────────────────
    try:
                    
        # if ano is not None:
        if ano is None:

            #Fazer o download do CSV do link: http://vitibrasil.cnpuv.embrapa.br/download/Producao.csv
            url_csv = 'http://vitibrasil.cnpuv.embrapa.br/download/Producao.csv'
            response = requests.get(url_csv, timeout=5)
            response.raise_for_status()
            
            # Pegar os CSV disponível no site
            df = pd.read_csv(io.StringIO(response.content.decode('utf-8')), sep=';')
                    
            # Passo 1: Identificar as colunas de anos
            anos = [str(ano) for ano in range(1970, datetime.datetime.now().year-1)]  # Pegar sempre o ano anterior ao atual

            # Passo 2: Derreter (melt) o DataFrame
            df_transformado = df.melt(
                id_vars=['control', 'produto'],
                value_vars=anos,
                var_name='Ano',
                value_name='Quantidade'
            )

            df_transformado['Categoria'] = df_transformado['control'].apply(extrair_categoria)
            df_transformado['Subcategoria'] = df_transformado.apply(
                lambda x: '' if x['control'] == x['produto'] else x['produto'],
                axis=1
            )

            #Excluir a coluna produto
            df_transformado.drop(columns=['produto'], inplace=True)

            #Renomear as colunas para ano, categoria, produto e quantidade
            df_transformado = df_transformado.rename(
                columns={
                    'Ano': 'ano',
                    'Categoria': 'categoria',
                    'Subcategoria': 'produto',
                    'Quantidade': 'quantidade'
                }
            )

            #Verificar na coluna produto se é vazio, se for, colocar "-"
            df_transformado['produto'] = df_transformado['produto'].replace('', '-')

            df_final = df_transformado[['ano', 'categoria', 'produto', 'quantidade']]
            df_final = df_final.sort_values(['ano', 'categoria', 'produto'])
            df_final = df_final.reset_index(drop=True)
            
            # Visualizar resultado
            return df_final.to_dict(orient="records")            

        #Se tem o parâmetro de ANO
        else:
            url = "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_02&ano="
            CLASSE_TABELA = {'class': 'tb_base tb_dados'}

            url = f"{url}{ano}"
            response = requests.get(url)
            response.raise_for_status()
            dados_ano = []

            #Fazer ir pro Exception se não conseguir pegar os dados    
            if response.status_code == 200:                
                soup = BeautifulSoup(response.text, 'html.parser')
                tabela = soup.find('table', CLASSE_TABELA)

                if not tabela:
                    print(f"[{ano}] Tabela não encontrada.")
                    return []

                linhas = tabela.find_all('tr')
                categoria_atual = None

                for linha in linhas:
                    colunas = linha.find_all('td')
                    if not colunas:
                        continue

                    primeira_coluna = colunas[0]

                    if 'tb_item' in primeira_coluna.get('class', []):
                        categoria_atual = primeira_coluna.text.strip()
                        quantidade = [col.text.strip() for col in colunas[1:]]

                        dados_ano.append([
                            ano,
                            categoria_atual,
                            "-",
                            int(quantidade[0].replace('.','')) if quantidade[0] != '-' else 0
                        ])
                    elif 'tb_subitem' in primeira_coluna.get('class', []):
                        produto = primeira_coluna.text.strip()
                        quantidade = [col.text.strip() for col in colunas[1:]]

                        dados_ano.append([
                            ano,
                            categoria_atual,
                            produto,
                            int(quantidade[0].replace('.','')) if quantidade[0] != '-' else 0
                        ])
            else:
                print("Não conseguiu pegar os dados")
                
            df_final_from_year = pd.DataFrame(dados_ano, columns=['ano', 'categoria', 'produto', 'quantidade'])
            return df_final_from_year.to_dict(orient="records")          

    except Exception as e:
        # Se qualquer erro ocorrer no bloco live, vamos ao fallback abaixo.
        print("Live scraping falhou, usando fallback CSV.")
        print(f"Erro: {e}")
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

if __name__ == "__main__":
    # Teste rápido para verificar se o fallback funciona
    try:
        producao = asyncio.run(buscar_producao(ano=2023))
        print(producao)
    except HTTPException as e:
        print(f"Erro: {e.detail}")
    except Exception as e:
        print(f"Erro inesperado: {e}")