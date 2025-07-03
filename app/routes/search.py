"""
Rotas para operações de busca.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from ..models import (
    SearchResponse, AutocompleteResponse, IndexResponse, 
    DeleteResponse, ProductCreate
)
from ..typesense_client import TypesenseClient, get_typesense_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["search"])


@router.get("/search", response_model=SearchResponse)
async def search_products(
    q: str = Query(..., description="Termo de busca"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    marca: Optional[str] = Query(None, description="Filtrar por marca"),
    preco_min: Optional[float] = Query(None, description="Preço mínimo", ge=0),
    preco_max: Optional[float] = Query(None, description="Preço máximo", ge=0),
    sort: Optional[str] = Query(None, description="Campo para ordenação (preco|avaliacao|relevancia)"),
    limit: int = Query(10, description="Número máximo de resultados", ge=1, le=100),
    offset: int = Query(0, description="Offset para paginação", ge=0),
    client: TypesenseClient = Depends(get_typesense_client)
):
    """
    Busca produtos no catálogo eletrônico.
    
    Suporta busca textual, filtros por categoria/marca/preço e ordenação.
    """
    try:
        # Validar range de preços
        if preco_min is not None and preco_max is not None and preco_max < preco_min:
            raise HTTPException(
                status_code=400, 
                detail="Preço máximo deve ser maior que o mínimo"
            )
        
        # Construir filtros
        filters = []
        if categoria:
            filters.append(f"categoria:{categoria}")
        if marca:
            filters.append(f"marca:{marca}")
        if preco_min is not None:
            filters.append(f"preco:>={preco_min}")
        if preco_max is not None:
            filters.append(f"preco:<={preco_max}")
        
        filter_str = " && ".join(filters) if filters else None
        
        # Mapear ordenação
        sort_mapping = {
            "preco": "preco:asc",
            "avaliacao": "avaliacao:desc",
            "relevancia": "_text_match:desc,avaliacao:desc"
        }
        sort_by = sort_mapping.get(sort) if sort else None
        
        # Executar busca
        result = await client.search_products(
            query=q,
            filters=filter_str,
            sort_by=sort_by,
            limit=limit,
            offset=offset
        )
        
        return SearchResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na busca: {e}")
        return SearchResponse(
            status="error",
            query=q,
            total=0,
            results=[],
            message=f"Erro interno: {str(e)}"
        )


@router.get("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete_products(
    q: str = Query(..., description="Prefixo para autocompletar", min_length=1),
    limit: int = Query(5, description="Número máximo de sugestões", ge=1, le=20),
    client: TypesenseClient = Depends(get_typesense_client)
):
    """
    Retorna sugestões de autocompletar para busca.
    
    Busca por prefixos em nomes de produtos e marcas.
    """
    try:
        result = await client.autocomplete(prefix=q, limit=limit)
        return AutocompleteResponse(**result)
        
    except Exception as e:
        logger.error(f"Erro no autocompletar: {e}")
        return AutocompleteResponse(
            status="error",
            prefix=q,
            suggestions=[],
            message=f"Erro interno: {str(e)}"
        )


@router.post("/index", response_model=IndexResponse)
async def index_product(
    product: ProductCreate,
    client: TypesenseClient = Depends(get_typesense_client)
):
    """
    Indexa um novo produto no catálogo de busca.
    
    Adiciona o produto na base Typesense para ser encontrado nas buscas.
    """
    try:
        # Converter para dict
        product_dict = product.model_dump()
        
        # Garantir que tem ID
        if not product_dict.get('id'):
            product_dict['id'] = product.id
        
        result = await client.index_document(product_dict)
        
        return IndexResponse(**result)
        
    except Exception as e:
        logger.error(f"Erro ao indexar produto: {e}")
        return IndexResponse(
            status="error",
            message=f"Erro interno: {str(e)}"
        )


@router.delete("/documents/{document_id}", response_model=DeleteResponse)
async def delete_product(
    document_id: str,
    client: TypesenseClient = Depends(get_typesense_client)
):
    """
    Remove um produto do catálogo de busca.
    
    Remove o produto da base Typesense.
    """
    try:
        result = await client.delete_document(document_id)
        return DeleteResponse(**result)
        
    except Exception as e:
        logger.error(f"Erro ao remover produto: {e}")
        return DeleteResponse(
            status="error",
            message=f"Erro interno: {str(e)}"
        ) 