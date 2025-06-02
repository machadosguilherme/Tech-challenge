# app/schemas/exportacao.py

from pydantic import BaseModel

class Exportacao(BaseModel):
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
                "paises": "Estados Unidos",
                "quantidade": 987654.0,
                "valor_us": 321098.0
            }
        }
