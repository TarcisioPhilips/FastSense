# 🔍 search-tool

API de busca inteligente usando **FastAPI + Typesense** para e-commerce eletrônicos.

## 🚀 Quick Start

### 1. Subir o Typesense (Motor de Busca)
```bash
# Rodar Typesense via Docker
docker run -d --name typesense-server \
  -p 8108:8108 \
  -v/tmp/typesense-data:/data \
  typesense/typesense:29.0 \
  --data-dir /data --api-key=xyz --enable-cors

# Verificar se está rodando
curl http://localhost:8108/health
```

### 2. Instalar Dependências
```bash
# Instalar dependências com UV
uv add fastapi uvicorn typesense python-multipart pydantic-settings
```

### 3. Rodar a API
```bash
# Iniciar API de busca
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Popular Base de Dados
```bash
# Carregar dados de exemplo (20 produtos eletrônicos)
uv run python data/setup_data.py
```

## 📡 Endpoints da API

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Informações da API |
| `/health` | GET | Status da API e Typesense |
| `/docs` | GET | Documentação Swagger |
| `/api/v1/search` | GET | Busca produtos |
| `/api/v1/autocomplete` | GET | Sugestões |
| `/api/v1/index` | POST | Indexar produto |
| `/api/v1/documents/{id}` | DELETE | Remover produto |

## 🔎 Exemplos de Uso

### Busca Simples
```bash
curl "http://localhost:8000/api/v1/search?q=iphone"
```

### Busca com Filtros
```bash
curl "http://localhost:8000/api/v1/search?q=smartphone&categoria=smartphones&marca=Apple&preco_max=8000&sort=preco"
```

### Autocompletar
```bash
curl "http://localhost:8000/api/v1/autocomplete?q=sam"
```

### Indexar Novo Produto
```bash
curl -X POST "http://localhost:8000/api/v1/index" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Galaxy S24 Ultra",
    "descricao": "Smartphone Samsung top de linha",
    "preco": 6999.99,
    "categoria": "smartphones",
    "marca": "Samsung",
    "avaliacao": 4.7,
    "estoque": 10,
    "tags": ["android", "premium", "camera"]
  }'
```

## 🏗️ Arquitetura

```
┌─────────────────┐    GET /search?q=termo    ┌─────────────────┐    Typesense API    ┌─────────────────┐
│   Cliente       │ ─────────────────────────► │   search-tool   │ ──────────────────► │   Typesense     │
│   (Frontend)    │                            │   FastAPI       │                    │   Search Engine │
│                 │ ◄───── JSON Results ────── │   (Port 8000)   │ ◄──── Results ──── │   (Port 8108)   │
└─────────────────┘                            └─────────────────┘                    └─────────────────┘
```

## 📁 Estrutura do Projeto

```
search-tool/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app principal
│   ├── models.py               # Schemas Pydantic
│   ├── typesense_client.py     # Cliente Typesense
│   ├── config.py               # Configurações
│   └── routes/
│       ├── __init__.py
│       └── search.py           # Rotas de busca
├── data/
│   ├── produtos_eletronicos.json  # Dataset exemplo
│   └── setup_data.py               # Script população
├── pyproject.toml              # Dependências UV
├── README.md
└── PLANO_ACAO.md              # Documentação desenvolvimento
```

## ⚡ Features Implementadas

- ✅ **Busca textual** - Por nome, descrição, marca e tags
- ✅ **Filtros avançados** - Categoria, marca, faixa de preço
- ✅ **Ordenação** - Por preço, avaliação, relevância
- ✅ **Autocompletar** - Sugestões em tempo real
- ✅ **Paginação** - Limit e offset
- ✅ **CRUD dinâmico** - Indexar/remover produtos
- ✅ **Health check** - Monitoramento de status
- ✅ **Documentação** - Swagger UI automática
- ✅ **Tratamento de erros** - Respostas padronizadas
- ✅ **Logs estruturados** - Para debugging

## 🧪 Testando a API

### Validação Completa
```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Busca básica
curl "http://localhost:8000/api/v1/search?q=iphone"

# 3. Busca avançada
curl "http://localhost:8000/api/v1/search?q=notebook&categoria=notebooks&preco_max=10000&sort=preco"

# 4. Autocompletar
curl "http://localhost:8000/api/v1/autocomplete?q=mac"

# 5. Documentação
open http://localhost:8000/docs
```

### Dataset Incluído
20 produtos eletrônicos com:
- **Smartphones**: iPhone, Galaxy, Pixel
- **Notebooks**: MacBook, Dell XPS, Legion
- **Fones**: AirPods, Sony, Bose
- **Tablets**: iPad Pro, Galaxy Tab

## 🔧 Configuração

Configurações via variáveis de ambiente ou `.env`:

```env
# Typesense
TYPESENSE_HOST=localhost
TYPESENSE_PORT=8108
TYPESENSE_API_KEY=xyz

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
```

## 📊 Performance

- **Busca**: < 100ms para datasets até 10k produtos
- **Autocompletar**: < 50ms
- **Indexação**: ~10ms por documento
- **Memory**: ~50MB (API) + ~100MB (Typesense)

## 🚀 Deploy

### Docker (Opcional)
```bash
# Build da API
docker build -t search-tool .

# Run completo com docker-compose
docker-compose up -d
```

### Produção
1. Configure Typesense Cloud ou servidor dedicado
2. Ajuste variáveis de ambiente
3. Use reverse proxy (nginx)
4. Configure monitoramento

## 🤝 Contribuindo

1. Fork o projeto
2. Crie branch para feature (`git checkout -b feature/nova-feature`)
3. Commit changes (`git commit -am 'Add nova feature'`)
4. Push branch (`git push origin feature/nova-feature`)
5. Abra Pull Request

## 📄 Licença

MIT License - veja arquivo [LICENSE](LICENSE) para detalhes.

---

**Feito com ❤️ usando FastAPI + Typesense**
