# app/routers/recurso.py

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.params import Depends

from app.crud.producao import buscar_producao
from app.crud.processamento import buscar_processamento
from app.crud.comercializacao import buscar_comercializacao
from app.crud.importacao import buscar_importacao
from app.crud.exportacao import buscar_exportacao

from app.schemas.producao import Producao
from app.schemas.processamento import Processamento
from app.schemas.comercializacao import Comercializacao
from app.schemas.importacao import Importacao
from app.schemas.exportacao import Exportacao

router = APIRouter(
    prefix="",
    tags=["dados"],
)

# Mapeamento recurso → (função CRUD, esquema pydantic)
MAP_RECURSOS = {
    "producao": {
        "crud": buscar_producao,
        "schema": Producao
    },
    "processamento": {
        "crud": buscar_processamento,
        "schema": Processamento
    },
    "comercializacao": {
        "crud": buscar_comercializacao,
        "schema": Comercializacao
    },
    "importacao": {
        "crud": buscar_importacao,
        "schema": Importacao
    },
    "exportacao": {
        "crud": buscar_exportacao,
        "schema": Exportacao
    },
}


@router.get(
    "/{recurso}/",
    summary="Retorna dados de vitivinicultura",
    description="recurso até: producao, processamento, comercializacao, importacao, exportacao",
    response_model=List[  # Lista de dicionários que obedecem ao schema correto
        # O ‘response_model’ só é resolvido em tempo de definição, então teremos de usar um hack:
        # - Em runtime, fastapi vai validar cada item usando schema_model
        # Como workaround, definimos “response_model=List[dict]” e validamos manualmente abaixo.
        dict  
    ],
)
async def listar_recurso(
    recurso: str,
    ano: Optional[int] = Query(None, description="Ano a filtrar")
):
    """
    1) Verifica se ‘recurso’ está no nosso MAP_RECURSOS.
    2) Se existir, chama a função CRUD correspondente: func_buscar(ano).
    3) Valida cada item do resultado contra o schema Pydantic.
    4) Retorna lista de dicts (já validados).
    """
    if recurso not in MAP_RECURSOS:
        raise HTTPException(status_code=404, detail="Recurso não encontrado")

    func_buscar = MAP_RECURSOS[recurso]["crud"]
    schema_model = MAP_RECURSOS[recurso]["schema"]

    # Executa a função CRUD (que tentará live + fallback)
    try:
        resultado: List[dict] = await func_buscar(ano)
    except HTTPException as he:
        # Repassa HTTPException (503, 500 etc.)
        raise he
    except Exception as e:
        # Erro inesperado no CRUD
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao buscar '{recurso}': {e}"
        )

    # Validação Pydantic item‐a‐item
    validated = []
    for item in resultado:
        try:
            obj = schema_model(**item)
            validated.append(obj.dict())
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro de validação no item: {item}. Detalhe: {e}"
            )

    return validated
