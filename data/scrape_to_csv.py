import requests
from bs4 import BeautifulSoup
import datetime
import pandas as pd
import time

def scrape_to_csv_producao(year):

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
                    "-",
                    quantidade[0]
                ])
            elif 'tb_subitem' in primeira_coluna.get('class', []):
                produto = primeira_coluna.text.strip()
                quantidade = [col.text.strip() for col in colunas[1:]]

                dados_ano.append([
                    year,
                    categoria_atual,
                    produto,
                    quantidade[0]
                ])
    else:
        print("Não conseguiu pegar os dados")
        
    return dados_ano

def scrape_to_csv_processamento(ano=None, sub='opt_01'):    
    
    url = f"http://vitibrasil.cnpuv.embrapa.br/index.php?ano={ano}&opcao=opt_03&subopcao={sub}"
    resposta = requests.get(url)

    if resposta.status_code == 200:
        soup = BeautifulSoup(resposta.text, 'html.parser')

        # Encontra a tabela (pode ajustar se tiver mais de uma tabela na página)
        tabela = soup.find('table', {'class': 'tb_base tb_dados'})

        if tabela:
            linhas = tabela.find_all('tr')
            dados = []
            categoria_atual = None
            
            for linha in linhas:
                colunas = linha.find_all('td')
                
                if not colunas:
                    continue  # Pula linhas vazias
                
                primeira_coluna = colunas[0]
                
                if 'tb_item' in primeira_coluna.get('class', []):
                    categoria_atual = primeira_coluna.text.strip()
                    dados.append({
                        'Categoria': categoria_atual,
                        'Cultivar': '-',
                        'Quantidade(Kg.)': [col.text.strip() for col in colunas[1:]]
                    })
                elif 'tb_subitem' in primeira_coluna.get('class', []):
                    produto = primeira_coluna.text.strip()
                    dados.append({
                        'Categoria': categoria_atual,
                        'Cultivar': produto,
                        'Quantidade(Kg.)': [col.text.strip() for col in colunas[1:]]
                    })
            
            return dados
        else:
            print(f"Nenhuma tabela encontrada para o ano {ano}")
            return None
    else:
        print(f"Erro ao acessar o ano {ano}: {resposta.status_code}")
        return None

def scrape_to_csv_comercializacao(year):

    url = "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_04&ano="
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
                    "-",
                    quantidade[0]
                ])
            elif 'tb_subitem' in primeira_coluna.get('class', []):
                produto = primeira_coluna.text.strip()
                quantidade = [col.text.strip() for col in colunas[1:]]

                dados_ano.append([
                    year,
                    categoria_atual,
                    produto,
                    quantidade[0]
                ])
    else:
        print("Não conseguiu pegar os dados")
        
    return dados_ano

def scrape_to_csv_importacao(ano=None, sub='opt_01'):

    url = "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_05&subopcao={}&ano={}".format(sub,ano)
    resposta = requests.get(url)
    dados_ano = []

    if resposta.status_code == 200:
        soup = BeautifulSoup(resposta.text, 'html.parser')
        tabela = soup.find('table', {'class': 'tb_base tb_dados'})

        if tabela:
            linhas = tabela.find_all('tr')
            categoria_atual = None

            for linha in linhas:
                colunas = linha.find_all('td')
                if not colunas:
                    continue

                primeira_coluna = colunas[0]
                pais = primeira_coluna.text.strip()
                quantidade = colunas[1].text.strip()
                valor = colunas[2].text.strip()

                dados_ano.append([
                    ano,
                    pais,
                    quantidade,
                    valor
                ])
            return dados_ano
    else:
        print(f"Erro ao acessar o ano {ano}: {resposta.status_code}")
        return None

def scrape_to_csv_exportacao(ano=None, sub='opt_01'):

    url = "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_06&subopcao={}&ano={}".format(sub,ano)
    resposta = requests.get(url)
    dados_ano = []

    if resposta.status_code == 200:
        soup = BeautifulSoup(resposta.text, 'html.parser')
        tabela = soup.find('table', {'class': 'tb_base tb_dados'})

        if tabela:
            linhas = tabela.find_all('tr')
            categoria_atual = None

            for linha in linhas:
                colunas = linha.find_all('td')
                if not colunas:
                    continue

                primeira_coluna = colunas[0]
                pais = primeira_coluna.text.strip()
                quantidade = colunas[1].text.strip()
                valor = colunas[2].text.strip()

                dados_ano.append([
                    ano,
                    pais,
                    quantidade,
                    valor
                ])
            return dados_ano
    else:
        print(f"Erro ao acessar o ano {ano}: {resposta.status_code}")
        return None


if __name__ == "__main__":

    years = range(1970, datetime.datetime.now().year - 1)
    # years = range(1970, 1972)
    #--------------------------------------------
    # Producao
    #--------------------------------------------
    list_producao = []

    for year in years:
        data = scrape_to_csv_producao(year)
        if(len(data)>0):
            list_producao.extend(data)
            time.sleep(1)
            print("Dados do ano {} extraído".format(year))

    if len(list_producao)>0:
        df = pd.DataFrame(list_producao, columns=[
            'Ano', 'Categoria', 'Produto', 'Quantidade(L.)'])
        df.to_csv('./data_test/producao.csv', index=False, encoding='utf-8', sep=',')    


    #--------------------------------------------
    # Processamento
    #--------------------------------------------
    subs_processamento = {
    'subopt_01': 'Viniferas',
    'subopt_02': 'Americanas e hibridas',
    'subopt_03': 'Uvas de mesa',
    'subopt_04': 'Sem classificação'
    }

    list_processamento = []
    for ano in years:
        for sub, desc in subs_processamento.items():
            print(f"Processando {desc} para o ano {ano}...")
            dados = scrape_to_csv_processamento(ano, sub)
            time.sleep(1) # Aguardar 1 segundo entre as requisições para evitar bloqueios
            if dados:
                for d in dados:
                    list_processamento.append([desc, ano, d['Categoria'], d['Cultivar'], d['Quantidade(Kg.)'][0]])

    if len(list_processamento)>0:
        #Colunas: Opção,Ano,Categoria,Cultivar,Quantidade(Kg.)

        df = pd.DataFrame(list_processamento, columns=[
            'Opção', 'Ano', 'Categoria', 'Cultivar', 'Quantidade(Kg.)'])
        df.to_csv('./data_test/processamento.csv', index=False, encoding='utf-8', sep=',')


    #--------------------------------------------
    # Importacao
    #--------------------------------------------
    subs_importacao = {
        'subopt_01': 'Vinhos de mesa',
        'subopt_02': 'Espumantes',
        'subopt_03': 'Uvas frescas',
        'subopt_04': 'Uvas passas',
        'subopt_05': 'Suco de uva'
    }
    list_importacao = []
    for ano in years:
        for sub, desc in subs_importacao.items():
            print("Processando {} para o ano {}...".format(desc, ano))
            dados = scrape_to_csv_importacao(ano, sub)
            time.sleep(1)  # Aguardar 1 segundo entre as requisições para evitar bloqueios
            if dados:
                for d in dados:
                    list_importacao.append([desc,d[0], d[1], d[2], d[3]])
    if len(list_importacao) > 0:
        # Colunas: Opção,Ano,Países,Quantidade(Kg.),Valor (US$)
        df = pd.DataFrame(list_importacao, columns=[
            'Opção', 'Ano','Países', 'Quantidade(Kg.)', 'Valor (US$)'])
        df.to_csv('./data_test/importacao.csv', index=False, encoding='utf-8', sep=',')

    #--------------------------------------------
    # Exportacao
    #--------------------------------------------
    subs_exportacao = {
        'subopt_01': 'Vinhos de mesa',
        'subopt_02': 'Espumantes',
        'subopt_03': 'Uvas frescas',
        'subopt_04': 'Suco de uva'
    }
    list_exportacao = []
    for ano in years:
        for sub, desc in subs_exportacao.items():
            print("Processando {} para o ano {}...".format(desc, ano))
            dados = scrape_to_csv_exportacao(ano, sub)
            time.sleep(1)  # Aguardar 1 segundo entre as requisições para evitar bloqueios
            if dados:
                for d in dados:
                    list_exportacao.append([desc,d[0], d[1], d[2], d[3]])
    if len(list_exportacao) > 0:
        # Colunas: Opção,Ano,Países,Quantidade(Kg.),Valor (US$)
        df = pd.DataFrame(list_exportacao, columns=[
            'Opção', 'Ano','Países', 'Quantidade(Kg.)', 'Valor (US$)'])
        df.to_csv('./data_test/exportacao.csv', index=False, encoding='utf-8', sep=',')


    #--------------------------------------------
    # Comercializacao
    #--------------------------------------------
    list_comercializacao = []
    for year in years:
        data = scrape_to_csv_comercializacao(year)
        if(len(data)>0):
            list_comercializacao.extend(data)
            time.sleep(1)
            print("Dados do ano {} extraído".format(year))
    if len(list_comercializacao)>0:
        df = pd.DataFrame(list_comercializacao, columns=[
            'Ano', 'Categoria', 'Produto', 'Quantidade(L)'])
        df.to_csv('./data_test/comercializacao.csv', index=False, encoding='utf-8', sep=',')
