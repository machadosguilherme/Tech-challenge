# app/schemas/recurso.py

from pydantic import BaseModel, ConfigDict

class Recurso(BaseModel):
    """
    Schema genérico que aceita qualquer chave (extra) e
    expõe um exemplo no OpenAPI.
    """
    # 1) Permite campos extras (não declarados)
    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {
                # Exemplo baseado nos seus CSVs
                "Ano": 1970,
                "Categoria": "VINHO DE MESA",
                "Produto": "Tinto",
                "Quantidade(L.)": 217208.604
            }
        }
    )
