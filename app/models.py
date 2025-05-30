from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ProducaoVinho(Base):
    __tablename__ = 'producao_vinhos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ano = Column(Integer, nullable=False)
    categoria = Column(String(100), nullable=False)
    subcategoria = Column(String(100), nullable=True)  # Pode ser NULL quando vazio
    quantidade = Column(Float, nullable=False)

    def __repr__(self):
        return f"<ProducaoVinho(ano={self.ano}, categoria='{self.categoria}', quantidade={self.quantidade})>"