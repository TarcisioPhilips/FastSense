"""
Modelos Pydantic para validação de dados da API.
"""

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, field_validator
import re


class ProductBase(BaseModel):
    """Modelo base para produto."""
    nome: str = Field(..., description="Nome do produto", min_length=1, max_length=200)
    descricao: str = Field(..., description="Descrição detalhada do produto", max_length=1000)
    preco: float = Field(..., description="Preço em reais", gt=0)
    categoria: str = Field(..., description="Categoria do produto", max_length=50)
    marca: str = Field(..., description="Marca do produto", max_length=50)
    avaliacao: float = Field(default=0.0, description="Avaliação média (0-5)", ge=0, le=5)
    estoque: int = Field(default=0, description="Quantidade em estoque", ge=0)
    tags: List[str] = Field(default_factory=list, description="Tags para classificação")


class ProductCreate(ProductBase):
    """Modelo para criação de produto."""
    id: Optional[str] = Field(None, description="ID do produto (gerado automaticamente se não fornecido)")
    
    @field_validator('id')
    @classmethod
    def generate_id_if_none(cls, v, info):
        """Gera ID baseado no nome se não fornecido."""
        if v is None:
            values = info.data
            if 'nome' in values:
                # Gera ID simples baseado no nome
                name = values['nome'].lower()
                clean_name = re.sub(r'[^\w\s]', '', name)
                clean_name = re.sub(r'\s+', '_', clean_name)
                return clean_name[:50]
        return v


class ProductResponse(ProductBase):
    """Modelo para resposta de produto."""
    id: str = Field(..., description="ID único do produto")
    
    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    """Modelo para resposta de busca."""
    status: str = Field(..., description="Status da busca (success/error)")
    query: str = Field(..., description="Termo buscado")
    total: int = Field(..., description="Total de resultados encontrados")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="Lista de produtos encontrados")
    filters: Optional[str] = Field(None, description="Filtros aplicados")
    message: Optional[str] = Field(None, description="Mensagem de erro, se houver")


class AutocompleteResponse(BaseModel):
    """Modelo para resposta de autocompletar."""
    status: str = Field(..., description="Status da operação")
    prefix: str = Field(..., description="Prefixo buscado")
    suggestions: List[str] = Field(default_factory=list, description="Lista de sugestões")
    message: Optional[str] = Field(None, description="Mensagem de erro, se houver")


class IndexResponse(BaseModel):
    """Modelo para resposta de indexação."""
    status: str = Field(..., description="Status da indexação")
    document: Optional[Dict[str, Any]] = Field(None, description="Documento indexado")
    message: Optional[str] = Field(None, description="Mensagem de erro ou sucesso")


class DeleteResponse(BaseModel):
    """Modelo para resposta de exclusão."""
    status: str = Field(..., description="Status da exclusão")
    deleted_id: Optional[str] = Field(None, description="ID do documento removido")
    message: Optional[str] = Field(None, description="Mensagem de erro ou sucesso")


class HealthResponse(BaseModel):
    """Modelo para resposta de health check."""
    status: str = Field(..., description="Status da API")
    api_status: str = Field(..., description="Status da API FastAPI")
    typesense_status: str = Field(..., description="Status da conexão com Typesense")
    typesense_info: Optional[Dict[str, Any]] = Field(None, description="Informações do Typesense")
    message: Optional[str] = Field(None, description="Mensagem adicional") 