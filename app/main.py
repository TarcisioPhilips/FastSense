"""
Aplicação principal search-tool.

API de busca inteligente usando FastAPI + Typesense.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import Settings, get_settings
from .models import HealthResponse
from .routes.search import router as search_router
from .typesense_client import TypesenseClient, get_typesense_client

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação."""
    # Startup
    logger.info("🚀 Iniciando search-tool API...")
    
    # Tentar criar collection de produtos
    client = get_typesense_client()
    collection_created = await client.create_products_collection()
    
    if collection_created:
        logger.info("✅ Collection de produtos configurada")
    else:
        logger.warning("⚠️ Erro ao configurar collection - Typesense pode não estar disponível")
    
    logger.info("✅ search-tool API iniciada com sucesso!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Finalizando search-tool API...")


def create_application() -> FastAPI:
    """Factory para criar a aplicação FastAPI."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Incluir routers
    app.include_router(search_router)
    
    return app


# Criar instância da aplicação
app = create_application()


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check(
    client: TypesenseClient = Depends(get_typesense_client)
):
    """
    Endpoint de health check.
    
    Verifica status da API e conectividade com Typesense.
    """
    try:
        # Verificar conexão com Typesense
        typesense_health = await client.health_check()
        
        if typesense_health["status"] == "ok":
            return HealthResponse(
                status="healthy",
                api_status="running",
                typesense_status="connected",
                typesense_info=typesense_health.get("typesense"),
                message="API e Typesense funcionando normalmente"
            )
        else:
            return HealthResponse(
                status="degraded",
                api_status="running",
                typesense_status="disconnected",
                message=f"API funcionando, mas Typesense indisponível: {typesense_health.get('message')}"
            )
            
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return HealthResponse(
            status="unhealthy",
            api_status="running",
            typesense_status="error",
            message=f"Erro interno: {str(e)}"
        )


@app.get("/", tags=["info"])
async def root():
    """Endpoint raiz com informações da API."""
    settings = get_settings()
    return {
        "name": settings.app_name,
        "description": settings.app_description,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "search": "/api/v1/search",
            "autocomplete": "/api/v1/autocomplete",
            "index": "/api/v1/index",
            "delete": "/api/v1/documents/{id}"
        }
    }


@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    """Handler para erros internos do servidor."""
    logger.error(f"Erro interno: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Erro interno do servidor",
            "detail": str(exc) if app.debug else "Erro interno"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info"
    ) 