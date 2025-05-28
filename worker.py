import pandas as pd
import datetime
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import numpy as np
import os
import io

def get_production_data_per_year(year):

    url = "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_02&ano="
    CLASSE_TABELA = {'class': 'tb_base tb_dados'}

    url = f"{url}{year}"
    resposta = requests.get(url)
    dados_ano = []

    if resposta.status_code == 200:
        soup = BeautifulSoup(resposta.text, 'html.parser')
        tabela = soup.find('table', CLASSE_TABELA)

        if not tabela:
            print(f"[{year}] Tabela não encontrada.")
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
                    year,
                    categoria_atual,
                    None,
                    int(quantidade[0].replace('.','')) if quantidade[0] != '-' else 0
                ])
            elif 'tb_subitem' in primeira_coluna.get('class', []):
                produto = primeira_coluna.text.strip()
                quantidade = [col.text.strip() for col in colunas[1:]]

                dados_ano.append([
                    year,
                    categoria_atual,
                    produto,
                    int(quantidade[0].replace('.','')) if quantidade[0] != '-' else 0
                ])
    else:
        print("Não conseguiu pegar os dados")
        

    return dados_ano

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
        return None

def get_production_data_from_csv():
    
    #Pegar os CSV disponível no site
    df = pd.read_csv('data/Producao.csv', sep=';')

    # Passo 1: Identificar as colunas de anos
    anos = [str(ano) for ano in range(1970, 2024)]  # Ajuste conforme suas colunas

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

    df_final = df_transformado[['Ano', 'Categoria', 'Subcategoria', 'Quantidade']]
    df_final = df_final.sort_values(['Ano', 'Categoria', 'Subcategoria'])
    df_final = df_final.reset_index(drop=True)


    # Visualizar resultado
    return df_final
    

if __name__ == "__main__":

    years = range(1970, datetime.datetime.now().year -1)
    list_tables = []

    for year in years:
        data = get_production_data_per_year(year)
        if(len(data)>0):
            list_tables.extend(data)
            time.sleep(1)
            print("Dados do ano {} extraído".format(year))

    if len(list_tables)>0:
        df = pd.DataFrame(list_tables, columns=['Ano', 'Categoria', 'Subcategoria', 'Quantidade']) 
        df.to_csv('./data/producao.csv', index=False, encoding='utf-8', sep=';')

    else:
        data = get_production_data_from_csv()
        data.to_csv('./data/producao_from_file.csv', sep=';', index=False, encoding='utf-8')



