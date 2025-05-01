# Flask API

Uma API simples construída com Flask.

## Configuração

1. Certifique-se de ter Python 3.8+ instalado
2. Ative o ambiente virtual:
   ```bash
   source .venv/bin/activate  # Linux/Mac
   # ou
   .venv\Scripts\activate  # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Executando a API

Para iniciar a API, execute:
```bash
python app.py
```

A API estará disponível em `http://localhost:5000`

## Endpoints

- `GET /`: Página inicial
- `GET /api/hello`: Retorna uma mensagem de saudação
- `POST /api/echo`: Recebe dados JSON e os retorna

## Exemplo de uso

```bash
# Teste o endpoint hello
curl http://localhost:5000/api/hello

# Teste o endpoint echo
curl -X POST -H "Content-Type: application/json" -d '{"teste":"dados"}' http://localhost:5000/api/echo
```

## Executando os Testes

Para executar os testes da API, use o comando:
```bash
pytest
```

Para ver mais detalhes sobre os testes, use:
```bash
pytest -v
```

Os testes incluem:
- Teste do endpoint da página inicial
- Teste do endpoint /api/hello
- Teste do endpoint /api/echo com dados válidos
- Teste do endpoint /api/echo com JSON inválido