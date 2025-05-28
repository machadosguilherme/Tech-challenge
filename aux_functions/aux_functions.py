import pandas as pd
import datetime
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os

def get_production_data_per_year(year):
    """
    Function to get production data for a specific year.
    """
    # URL base do site
    url = f"http://vitibrasil.cnpuv.embrapa.br/index.php?ano={year}&opcao=opt_02"

    # Parâmetros da requisição (opcao=opt_02 para a página de produção)
    params = {
        "opcao": "opt_02"
    }

    try:
        # Fazendo a requisição GET
        response = requests.get(url, params=params)
        response.raise_for_status()  # Verifica se houve erro na requisição
        
        # Parseando o HTML com BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Exemplo de extração de dados - tabela de produção
        tabela_producao = soup.find('table', {'class': 'tb_base tb_dados'})

        if tabela_producao:
            dados_organizados = {
                "products": [],
                "total": None,
            }

            item_atual = None

            for linha in tabela_producao.find_all('tr'):
                colunas = linha.find_all(['td', 'th'])
                
                # Pular cabeçalho
                if colunas[0].name == 'th':
                    continue
                    
                # Verificar classes das células
                classes = colunas[0].get('class', [])
                
                if 'tb_item' in classes:
                    item_atual = {
                        "nome": colunas[0].get_text(strip=True),
                        "quantity": int(colunas[1].get_text(strip=True).replace('.', '')) if colunas[1].get_text(strip=True) != '-' else 0,
                        "subitens": []
                    }
                    dados_organizados["products"].append(item_atual)
                    
                elif 'tb_subitem' in classes and item_atual is not None:
                    subitem = {
                        "type": colunas[0].get_text(strip=True),
                        "quantity": int(colunas[1].get_text(strip=True).replace('.', '')) if colunas[1].get_text(strip=True) != '-' else 0
                    }
                    item_atual["subitens"].append(subitem)
                    
                elif not classes and 'Total' in colunas[0].get_text():
                    dados_organizados["total"] = int(colunas[1].get_text(strip=True).replace('.', ''))

            return dados_organizados

        else:
            print("Tabela de produção não encontrada no HTML.")

    except requests.exceptions.RequestException as e:
        print(f"Erro ao fazer a requisição: {e}")
        return {}

    except Exception as e:
        print(f"Erro inesperado: {e}")

def get_production_data_from_csv():
    """
    Function to get production data from downloaded CSV file.
    """

    #Transformar em dataframe
    data = pd.read_csv('data/Producao.csv', sep=';')

    """
    Função definitiva que corrige os problemas de quantidade zerada/nula.
    Garante que as quantidades das categorias sejam preenchidas corretamente.
    """
    # Mapeamento completo de categorias
    CATEGORIAS = {
        "vm": {
            "nome": "VINHO DE MESA",
            "produto_principal": "VINHO DE MESA"
        },
        "vv": {
            "nome": "VINHO FINO DE MESA (VINIFERA)",
            "produto_principal": "VINHO FINO DE MESA (VINIFERA)"
        },
        "su": {
            "nome": "SUCO",
            "produto_principal": "SUCO"
        },
        "de": {
            "nome": "DERIVADOS",
            "produto_principal": "DERIVADOS"
        }
    }

    # Inverter o mapeamento para busca pelo nome do produto principal
    PRODUTOS_PRINCIPAIS = {v["produto_principal"]: k for k, v in CATEGORIAS.items()}

    # Estrutura final
    resultado = {"anos": {}}

    # Obter lista de anos
    anos = [col for col in data.columns[3:] if col.isdigit()]

    # Primeiro: criar estrutura para todos os anos e categorias
    for ano in anos:
        ano_int = int(ano)
        resultado["anos"][ano_int] = {
            "categorias": {
                cat_info["nome"]: {
                    "quantidade": 0,  # Inicializa com 0
                    "subprodutos": []
                } for cat, cat_info in CATEGORIAS.items()
            }
        }

    # Processar cada linha do DataFrame
    for _, row in data.iterrows():
        control = row['control']
        produto_nome = row['produto']
        
        # Verificar se é um produto principal (nome do produto está no mapeamento)
        if produto_nome in PRODUTOS_PRINCIPAIS:
            categoria_key = PRODUTOS_PRINCIPAIS[produto_nome]
            categoria_nome = CATEGORIAS[categoria_key]["nome"]
            
            for ano in anos:
                ano_int = int(ano)
                quantidade = row[ano] if pd.notna(row[ano]) else 0
                
                # Atualizar quantidade da categoria
                resultado["anos"][ano_int]["categorias"][categoria_nome]["quantidade"] = quantidade
        
        # Verificar se é um subproduto (contém underscore)
        elif '_' in control:
            prefixo = control.split('_')[0]
            if prefixo not in CATEGORIAS:
                continue
                
            categoria_nome = CATEGORIAS[prefixo]["nome"]
            
            for ano in anos:
                ano_int = int(ano)
                quantidade = row[ano] if pd.notna(row[ano]) else 0
                
                # Adicionar subproduto
                resultado["anos"][ano_int]["categorias"][categoria_nome]["subprodutos"].append({
                    "nome": produto_nome,
                    "quantidade": quantidade
                })

    return resultado

if __name__ == "__main__":    
    pass    

