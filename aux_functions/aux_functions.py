import pandas as pd
import datetime
import json
import requests
from bs4 import BeautifulSoup

def convert_data_to_api(original_data):
    """
    Função para converter os dados do DataFrame em um formato adequado para a API.
    Corrige os problemas de duplicação e estrutura hierárquica.
    """
    # Criar estrutura hierárquica
    resultado = {
        "categorias": []
    }

    #Controles
    controles = original_data['control'].loc[original_data['control'].str.contains('_')].unique()

    # Criar dicionário para armazenar os dados dos produtos principais com seus subprodutos
    categorias = {}
    for controle in controles:
        if 'vm_' in controle:
            #Vinho de mesa
            categorias['VINHO DE MESA'] = "vm"
        elif 'vv_' in controle:
            #Vinho de mesa
            categorias['VINHO FINO DE MESA (VINIFERA)'] = "vv"
        elif 'su_' in controle:
            #Suco
            categorias['SUCO'] = "su"
        elif 'de_' in controle:
            #Destilado
            categorias['DESTILADO'] = "de"

    # Dicionário para mapear produtos principais e seus subprodutos
    produtos_map = {}

    # Primeiro passada: identificar todos os produtos principais e criar estrutura básica
    for index, row in original_data.iterrows():
        control = row['control']
        produto = row['produto']
        
        # Verificar se é um produto principal (não contém underscore)
        if '_' not in control:    
            if control not in produtos_map:
                produtos_map[control] = {
                    'nome': produto,
                    'dados_historicos': [],
                    'subprodutos': [],
                    'categoria': categorias.get(control)
                }
                
                # Adicionar dados históricos
                for ano in original_data.columns[3:]:  # Colunas de anos
                    produtos_map[control]['dados_historicos'].append({
                        'ano': int(ano),
                        'quantidade': row[ano] if pd.notna(row[ano]) else None,                        
                    })
        
        #É um subproduto
        else:
            #O produto pai é a chave do control.split('_')[0]
            produto_pai = ""          
            if produto_pai in produtos_map:
                subproduto = {
                    'nome': produto,
                    'dados_historicos': []
                }
                
                # Adicionar dados históricos do subproduto
                for ano in original_data.columns[3:]:
                    subproduto['dados_historicos'].append({
                        'ano': int(ano),
                        'quantidade': row[ano] if pd.notna(row[ano]) else None
                    })


    # Organizar por categorias (grupos de produtos principais)
    categorias = set()
    for control in produtos_map.keys():
        categoria = control.split('_')[0] if '_' in control else control
        categorias.add(categoria)
    
    for categoria in sorted(categorias):
        cat_dict = {
            'nome': categoria,
            'produtos': []
        }
        
        # Adicionar produtos desta categoria
        for control, produto_data in produtos_map.items():
            if control.startswith(categoria) or control == categoria:
                cat_dict['produtos'].append(produto_data)
        
        resultado['categorias'].append(cat_dict)

    return resultado


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

def get_production_data():
    """
    Function to get production data from downloaded CSV file.
    """

    # Fazer o download do csv do seguinte site: http://vitibrasil.cnpuv.embrapa.br/download/Producao.csv
    url = "http://vitibrasil.cnpuv.embrapa.br/download/Producao.csv"
    response = requests.get(url)

    # Salvar em arquivo
    with open('data/Producao.csv', 'wb') as file:
        file.write(response.content)

    #Transformar em dataframe
    data = pd.read_csv('data/Producao.csv', sep=';')
    result = convert_data_to_api(data)
    
    #Ler o Dataframe
    return result

if __name__ == "__main__":
    
    #Read the file from data folder
    # with open('data/Producao.csv', 'r') as file:
    #     data = pd.read_csv('data/Producao.csv', sep=';')            

    data = get_production_data()

    #Convert to json
    result = data.to_dict(orient='records')
    convert_data_to_api(result)
