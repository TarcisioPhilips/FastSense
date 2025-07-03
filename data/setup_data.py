#!/usr/bin/env python3
"""
Script para popular dados de exemplo no Typesense.

Carrega produtos eletrônicos e indexa no Typesense para testes.
"""

import json
import asyncio
import sys
import os

# Adicionar o diretório raiz ao path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.typesense_client import get_typesense_client


async def load_sample_data():
    """Carrega dados de exemplo no Typesense."""
    print("🚀 Iniciando carregamento de dados de exemplo...")
    
    # Carregar dados do JSON
    try:
        with open('data/produtos_eletronicos.json', 'r', encoding='utf-8') as f:
            produtos = json.load(f)
        print(f"✅ Carregados {len(produtos)} produtos do arquivo JSON")
    except FileNotFoundError:
        print("❌ Arquivo produtos_eletronicos.json não encontrado!")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao decodificar JSON: {e}")
        return False
    
    # Obter cliente Typesense
    client = get_typesense_client()
    
    # Verificar conexão
    health = await client.health_check()
    if health["status"] != "ok":
        print(f"❌ Typesense não está disponível: {health.get('message', 'Erro desconhecido')}")
        print("💡 Certifique-se de que o Typesense está rodando:")
        print("   docker run -d --name typesense-server -p 8108:8108 \\")
        print("     -v/tmp/typesense-data:/data typesense/typesense:29.0 \\")
        print("     --data-dir /data --api-key=xyz --enable-cors")
        return False
    
    print("✅ Typesense conectado com sucesso!")
    
    # Criar collection (se não existir)
    collection_created = await client.create_products_collection()
    if not collection_created:
        print("❌ Erro ao criar collection de produtos")
        return False
    
    print("✅ Collection de produtos configurada")
    
    # Indexar produtos
    success_count = 0
    error_count = 0
    
    print(f"\n📦 Indexando {len(produtos)} produtos...")
    
    for i, produto in enumerate(produtos, 1):
        try:
            result = await client.index_document(produto)
            if result["status"] == "success":
                success_count += 1
                print(f"✅ {i:2d}/{len(produtos)} - {produto['nome']}")
            else:
                error_count += 1
                print(f"❌ {i:2d}/{len(produtos)} - Erro ao indexar {produto['nome']}: {result.get('message', 'Erro desconhecido')}")
        except Exception as e:
            error_count += 1
            print(f"❌ {i:2d}/{len(produtos)} - Exceção ao indexar {produto['nome']}: {e}")
    
    print(f"\n📊 Resultado da indexação:")
    print(f"   ✅ Sucessos: {success_count}")
    print(f"   ❌ Erros: {error_count}")
    print(f"   📈 Taxa de sucesso: {(success_count / len(produtos)) * 100:.1f}%")
    
    if success_count > 0:
        print(f"\n🎉 Base de dados populada com sucesso!")
        print(f"💡 Agora você pode testar a API:")
        print(f"   curl \"http://localhost:8000/api/v1/search?q=iphone\"")
        print(f"   curl \"http://localhost:8000/api/v1/autocomplete?q=sam\"")
        return True
    else:
        print(f"\n❌ Nenhum produto foi indexado com sucesso!")
        return False


if __name__ == "__main__":
    # Executar o script
    success = asyncio.run(load_sample_data())
    
    if success:
        print("\n✅ Script executado com sucesso!")
        sys.exit(0)
    else:
        print("\n❌ Script falhou!")
        sys.exit(1) 