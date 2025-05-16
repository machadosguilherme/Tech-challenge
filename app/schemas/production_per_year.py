from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class ProductionYearQuery(BaseModel):
    """
    Parâmetros de consulta para produção por ano
    
    Attributes:
        year: Ano da produção (1901-2999)
    """
    year: int = Field(
        ...,
        gt=1900,
        lt=3000,
        description="Ano da produção (ex: 2023)",
        examples=[2023]
        )

    @field_validator('year')
    def validate_year(cls, value):
        current_year = datetime.now().year + 1000
        if value > current_year:
            raise ValueError(f"Ano não pode ser maior que {current_year}")
        if value < 1901:
            raise ValueError("Ano não pode ser menor que 1901")
        return value

class ProductionItem(BaseModel):
    """
    Modelo de item de produção
    
    Attributes:
        id: Identificador único
        produto: Nome do produto
        quantidade: Quantidade produzida
        ano: Ano da produção
        estado: Sigla do estado
        created_at: Data de criação do registro
    """
    id: int
    produto: str
    quantidade: float
    ano: int
    estado: str
    created_at: Optional[datetime] = None

class ProductionResponse(BaseModel):
    """
    Resposta padrão da API para endpoints de produção
    
    Attributes:
        message: Mensagem descritiva
        data: Lista de itens de produção
        year: Ano consultado (opcional)
        status: Código de status HTTP
    """
    message: str
    data: List[Dict[str, Any]] | List[ProductionItem] | Dict[str, Any] = None
    year: Optional[int] = None
    status: int = 200

class ErrorResponse(BaseModel):
    """
    Resposta padrão para erros
    
    Attributes:
        message: Mensagem de erro
        status: Código de status HTTP
        details: Detalhes adicionais (opcional)
    """
    message: str
    status: int
    details: Optional[str] = None