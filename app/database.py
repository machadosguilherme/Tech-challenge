from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Carregar variáveis de ambiente
USER = os.getenv('DB_USER')
PASSWORD=os.getenv('DB_PASS')
DATABASE=os.getenv('DB_NAME')
DB_HOST=os.getenv('DB_HOST')

# Configuração para desenvolvimento local
DATABASE_URL = "postgresql://{}:{}@{}:5432/{}".format(USER,PASSWORD,DB_HOST,DATABASE)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()