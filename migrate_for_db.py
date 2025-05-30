import csv
from app.database import SessionLocal, engine
from app.models import Base, ProducaoVinho

def migrate_producao():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        with open('data/producao.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                # Converter string vazia em None para subcategoria
                subcategoria = row['Subcategoria'] if row['Subcategoria'] else None
                
                db.add(ProducaoVinho(
                    ano=int(row['Ano']),
                    categoria=row['Categoria'],
                    subcategoria=subcategoria,
                    quantidade=float(row['Quantidade'])
                ))
        db.commit()
        print("Migração concluída com sucesso!")
    except Exception as e:
        db.rollback()
        print(f"Erro durante migração: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate_producao()