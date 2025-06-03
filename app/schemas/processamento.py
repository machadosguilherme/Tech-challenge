# app/schemas/processamento.py

from pydantic import BaseModel

class Processamento(BaseModel):
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
                "quantidade": 1234567.0
            }
        }
