import pandas as pd
import requests
from bs4 import BeautifulSoup

def convert_data_to_api(original_data):

    transoformed_data = []

    for item in original_data:
        new_item = {
            'id': item['id'],
            'control': item['control'],
            'product': item['produto'],
            'years': {}
        }
        
        new_item['years'] = {
            k: v for k, v in item.items() 
            if k not in ['id', 'control', 'product'] and k.isdigit() and len(k) == 4
        }
        
        transoformed_data.append(new_item)
    
    return transoformed_data

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

if __name__ == "__main__":
    
    #Read the file from data folder
    with open('data/Producao.csv', 'r') as file:
        data = pd.read_csv('data/Producao.csv', sep=';')            

    #Convert to json
    result = data.to_dict(orient='records')
    convert_data_to_api(result)
