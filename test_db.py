from app.database import engine

try:
    conn = engine.connect()
    print("✅ Conexão com o PostgreSQL estabelecida com sucesso!")
    conn.close()
except Exception as e:
    print("❌ Falha na conexão com o PostgreSQL:")
    print(e)