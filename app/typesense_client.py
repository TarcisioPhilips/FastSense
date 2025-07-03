"""
Cliente Typesense para operações de busca e indexação.
"""

import logging
from typing import Dict, List, Any, Optional

import typesense
from typesense.exceptions import TypesenseClientError

from .config import settings

logger = logging.getLogger(__name__)


class TypesenseClient:
    """Cliente centralizado para operações com Typesense."""
    
    def __init__(self):
        """Inicializa o cliente Typesense."""
        self.client = typesense.Client({
            'nodes': [{
                'host': settings.typesense_host,
                'port': settings.typesense_port,
                'protocol': settings.typesense_protocol
            }],
            'api_key': settings.typesense_api_key,
            'connection_timeout_seconds': settings.typesense_timeout
        })
        
    async def health_check(self) -> Dict[str, Any]:
        """Verifica se o Typesense está acessível."""
        try:
            # Tentar fazer uma operação simples para verificar conectividade
            collections = self.client.collections.retrieve()
            return {"status": "ok", "typesense": {"collections": len(collections)}}
        except Exception as e:
            logger.error(f"Erro na conexão com Typesense: {e}")
            return {"status": "error", "message": str(e)}
    
    async def create_products_collection(self) -> bool:
        """Cria a collection de produtos se não existir."""
        schema = {
            'name': settings.products_collection,
            'fields': [
                {'name': 'id', 'type': 'string'},
                {'name': 'nome', 'type': 'string'},
                {'name': 'descricao', 'type': 'string'},
                {'name': 'preco', 'type': 'float'},
                {'name': 'categoria', 'type': 'string', 'facet': True},
                {'name': 'marca', 'type': 'string', 'facet': True},
                {'name': 'avaliacao', 'type': 'float'},
                {'name': 'estoque', 'type': 'int32'},
                {'name': 'tags', 'type': 'string[]', 'facet': True}
            ],
            'default_sorting_field': 'avaliacao'
        }
        
        try:
            self.client.collections.create(schema)
            logger.info(f"Collection '{settings.products_collection}' criada com sucesso")
            return True
        except TypesenseClientError as e:
            if "already exists" in str(e):
                logger.info(f"Collection '{settings.products_collection}' já existe")
                return True
            else:
                logger.error(f"Erro ao criar collection: {e}")
                return False
        except Exception as e:
            logger.error(f"Erro inesperado ao criar collection: {e}")
            return False
    
    async def index_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Indexa um documento na collection de produtos."""
        try:
            result = self.client.collections[settings.products_collection].documents.create(document)
            logger.info(f"Documento indexado: {document.get('id', 'sem_id')}")
            return {"status": "success", "document": result}
        except Exception as e:
            logger.error(f"Erro ao indexar documento: {e}")
            return {"status": "error", "message": str(e)}
    
    async def search_products(
        self, 
        query: str, 
        filters: Optional[str] = None,
        sort_by: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Busca produtos na collection."""
        try:
            search_params = {
                'q': query,
                'query_by': 'nome,descricao,marca,tags',
                'per_page': limit,
                'page': (offset // limit) + 1,
                'sort_by': sort_by or '_text_match:desc,avaliacao:desc'
            }
            
            if filters:
                search_params['filter_by'] = filters
                
            results = self.client.collections[settings.products_collection].documents.search(search_params)
            
            return {
                "status": "success",
                "results": results.get('hits', []),
                "total": results.get('found', 0),
                "query": query,
                "filters": filters
            }
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return {
                "status": "error", 
                "message": str(e),
                "results": [],
                "total": 0,
                "query": query,
                "filters": filters
            }
    
    async def autocomplete(self, prefix: str, limit: int = 5) -> Dict[str, Any]:
        """Busca por autocompletar baseado em prefixo."""
        try:
            search_params = {
                'q': prefix,
                'query_by': 'nome,marca',
                'per_page': limit,
                'prefix': True,
                'sort_by': 'avaliacao:desc'
            }
            
            results = self.client.collections[settings.products_collection].documents.search(search_params)
            
            # Extrair sugestões únicas
            suggestions = []
            seen = set()
            
            for hit in results.get('hits', []):
                doc = hit.get('document', {})
                nome = doc.get('nome', '')
                marca = doc.get('marca', '')
                
                # Adicionar nome se relevante
                if nome.lower().startswith(prefix.lower()) and nome.lower() not in seen:
                    suggestions.append(nome)
                    seen.add(nome.lower())
                    
                # Adicionar marca se relevante  
                if marca.lower().startswith(prefix.lower()) and marca.lower() not in seen:
                    suggestions.append(marca)
                    seen.add(marca.lower())
                    
                if len(suggestions) >= limit:
                    break
            
            return {
                "status": "success",
                "suggestions": suggestions[:limit],
                "prefix": prefix
            }
        except Exception as e:
            logger.error(f"Erro no autocompletar: {e}")
            return {
                "status": "error",
                "message": str(e),
                "suggestions": [],
                "prefix": prefix
            }
    
    async def delete_document(self, document_id: str) -> Dict[str, Any]:
        """Remove um documento da collection."""
        try:
            self.client.collections[settings.products_collection].documents[document_id].delete()
            logger.info(f"Documento removido: {document_id}")
            return {"status": "success", "deleted_id": document_id}
        except Exception as e:
            logger.error(f"Erro ao remover documento: {e}")
            return {"status": "error", "message": str(e)}


# Instância global do cliente
typesense_client = TypesenseClient()


def get_typesense_client() -> TypesenseClient:
    """Dependency injection para FastAPI."""
    return typesense_client 