# scripts/test_scrapers.py

import sys, os

# ────────────────────────────────────────────────────────────────────────────────
# Insere a raiz do projeto no PYTHONPATH para importar 'app'
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
# ────────────────────────────────────────────────────────────────────────────────

from app.ingestion.scrapers import scrape_producao, scrape_comercializacao

def main():
    print("=== Produção ===")
    print(scrape_producao().head(), "\n")
    print("=== Comercialização ===")
    print(scrape_comercializacao().head())

if __name__ == "__main__":
    main()
