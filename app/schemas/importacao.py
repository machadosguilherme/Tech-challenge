# app/schemas/importacao.py

from pydantic import BaseModel

class Importacao(BaseModel):
    opcao: str
    ano: int
    paises: str
    quantidade: float
    valor_us: float

    class Config:
        json_schema_extra = {
            "example": {
                "opcao": "Vinhos de mesa",
                "ano": 2022,
                "paises": "França",
                "quantidade": 123456.0,
                "valor_us": 789012.0
            }
        }
