# app/schemas/producao.py

from pydantic import BaseModel

class Producao(BaseModel):
    ano: int
    categoria: str
    produto: str
    quantidade: float

    class Config:
        # Ajuste para pydantic V2
        json_schema_extra = {
            "example": {
                "ano": 2022,
                "categoria": "VINHO DE MESA",
                "produto": "Tinto",
                "quantidade": 162844214.0
            }
        }
