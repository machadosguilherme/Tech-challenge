# app/schemas/comercializacao.py

from pydantic import BaseModel

class Comercializacao(BaseModel):
    ano: int
    categoria: str
    produto: str
    quantidade: float

    class Config:
        json_schema_extra = {
            "example": {
                "ano": 2022,
                "categoria": "VINHO DE MESA",
                "produto": "Tinto",
                "quantidade": 83300735.0
            }
        }
