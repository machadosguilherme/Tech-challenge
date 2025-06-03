# Tech-challenge
# API Vinicultura Embrapa

Este repositório contém uma API REST para disponibilizar dados de vitivinicultura (produção, processamento, comercialização, importação e exportação) a partir dos relatórios da Embrapa. Caso o scraping “ao vivo” (live scraping) do site da Embrapa falhe, a API recorre a arquivos CSV de fallback (pré-gerados) armazenados localmente. Além disso, há um health-check para monitorar a disponibilidade dos dados e uma aplicação Streamlit que consome a API e exibe gráficos e tabelas interativas.

---

## Funcionalidades Principais

- **Scraping “ao vivo”**  
  Utiliza `pandas.read_html` para extrair tabelas diretamente do site da Embrapa.
- **Fallback para CSV**  
  Se o site estiver indisponível ou o formato da tabela mudar, carrega-se um CSV local com os dados históricos.
- **Endpoints CRUD** para cada recurso:
  - `/producao/`
  - `/processamento/`
  - `/comercializacao/`
  - `/importacao/`
  - `/exportacao/`
- **Autenticação JWT**  
  Todas as rotas de dados são protegidas por token Bearer (JWT).
- **Health-check**  
  Rota `/healthz/` que verifica:
  1. Conectividade “ao vivo” (tentativa de scraping).
  2. Existência dos arquivos CSV de fallback.
- **Dashboard Streamlit**  
  Consome a API (com autenticação) e exibe:
  1. Tabela com os registros retornados (filtrados por ano).
  2. Gráfico de série temporal (evolução de quantidade por ano).
  3. Gráfico de barras (top-10 países, quando aplicável).
  4. Botão para download do CSV filtrado.

---

## Pré-Requisitos

- **Python 3.9+** (testado em 3.11)  
- **Git** (para clonar o repositório, opcional)  
- **Ambiente virtual** (recomendado: `venv` ou `conda`)  

### Dependências da API

```text
fastapi
uvicorn[standard]
pandas
python-jose[cryptography]
pytest
python-multipart       # necessário para OAuth2PasswordRequestForm
```

### Rodar a API Local

1. Clone o repositório:
   ```bash
    git clone https://github.com/machadosguilherme/Tech-challenge.git
    cd Tech-challenge
    ```
2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Configuração do ambiente:
  Na raiz do projeto, crie um arquivo `.env` com as informações que estão no arquivo `.env.example`:    
    ```text
    API_SECRET_KEY=your_secret_key
    ADMIN_USERNAME=admin
    ADMIN_PASSWORD=password
    ```
5. Execute a API:
    ```bash
    uvicorn app.main:app --reload
    ```
6. Acesse a documentação interativa da API (Swagger) em:
    ```
    http://localhost:8000/docs
    ```
7. Acessar o Streamlit:
    ```
    cd dashboard
    streamlit run streamlit_app.py    
    http://localhost:8501
    ```
