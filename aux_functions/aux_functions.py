import pandas as pd

def transformar_dados(dados_originais):

    dados_transformados = []

    for item in dados_originais:
        # Extrai os campos fixos
        novo_item = {
            'id': item['id'],
            'control': item['control'],
            'produto': item['produto'],
            'dados_historicos': {}
        }
        
        # Filtra e adiciona os anos (considerando que todas outras chaves são anos)
        novo_item['dados_historicos'] = {
            k: v for k, v in item.items() 
            if k not in ['id', 'control', 'produto'] and k.isdigit() and len(k) == 4
        }
        
        dados_transformados.append(novo_item)
    
    return dados_transformados

    


if __name__ == "__main__":
    
    #Read the file from data folder
    with open('data/Producao.csv', 'r') as file:
        data = pd.read_csv('data/Producao.csv', sep=';')            

    #Convert to json
    result = data.to_dict(orient='records')
    transformar_dados(result)
