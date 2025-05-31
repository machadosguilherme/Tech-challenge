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
