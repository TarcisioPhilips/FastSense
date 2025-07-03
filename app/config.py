"""
Configurações da aplicação search-tool.
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação."""
    
    # API Settings
    app_name: str = "search-tool"
    app_description: str = "API de busca inteligente usando FastAPI + Typesense"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # Typesense Settings
    typesense_host: str = "localhost"
    typesense_port: int = 8108
    typesense_protocol: str = "http"
    typesense_api_key: str = "xyz"
    typesense_timeout: int = 5
    
    # Collection Settings
    products_collection: str = "produtos"
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instância global das configurações
settings = Settings()


def get_settings() -> Settings:
    """Dependency injection para FastAPI."""
    return settings 