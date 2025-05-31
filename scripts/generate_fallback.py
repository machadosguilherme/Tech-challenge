# scripts/generate_fallback.py

import sys
import os
import pandas as pd

# ────────────────────────────────────────────────────────────────────────────────
# Garante que o diretório raiz do projeto esteja no PYTHONPATH
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
# ────────────────────────────────────────────────────────────────────────────────

def main():
    data_dir = os.path.join(ROOT, "data")
    fallback_path = os.path.join(data_dir, "producao.csv")

    # 1) Verifica se o CSV de fallback existe
    if not os.path.exists(fallback_path):
        print(f"⚠ CSV de fallback não encontrado: {fallback_path}")
        print("   Por favor, crie manualmente o arquivo em data/producao.csv")
        return

    # 2) Lê e exibe um preview
    print(f"✔ Usando CSV de fallback em: {fallback_path}\n")
    try:
        df = pd.read_csv(fallback_path)
        print("Preview do CSV de fallback:")
        print(df.head().to_string(index=False))
    except Exception as e:
        print(f"✖ Erro ao ler o CSV de fallback: {e}")

if __name__ == "__main__":
    main()
