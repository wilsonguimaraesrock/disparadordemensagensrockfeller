# 🚀 Evolution API - Alternativa ao WAHA Core

## 📋 Visão Geral

A **Evolution API** é uma excelente alternativa ao WAHA Core para envio de mensagens e mídia via WhatsApp. Este guia demonstra como configurar e usar a Evolution API para substituir o WAHA Core em seu projeto de disparador de mensagens em lote.

## ✅ Vantagens da Evolution API

- 🆓 **Gratuita e Open Source**
- 🐳 **Fácil instalação com Docker**
- 🌐 **Interface web intuitiva**
- 📱 **Suporte completo a mídia** (imagens, vídeos, documentos, áudios)
- 🔄 **API REST simples e bem documentada**
- 🛡️ **Estável e confiável**
- 🔧 **Configuração flexível**

## 🔧 Configuração Atual

### Docker Compose
A Evolution API já está configurada no seu `docker-compose.yml`:

```yaml
services:
  evolution_api:
    image: atendai/evolution-api:v2.1.1
    container_name: evolution_api
    ports:
      - "8080:8080"
    environment:
      - SERVER_TYPE=http
      - SERVER_PORT=8080
      - CORS_ORIGIN=*
      - CORS_METHODS=GET,POST,PUT,DELETE
      - CORS_CREDENTIALS=true
      - LOG_LEVEL=ERROR
      - LOG_COLOR=true
      - LOG_BAILEYS=error
      - DEL_INSTANCE=false
      - PROVIDER_HOST=http://localhost:8080
      - PROVIDER_PORT=8080
      - DATABASE_ENABLED=true
      - DATABASE_CONNECTION_URI=postgresql://evolution:evolution@evolution_postgres:5432/evolution
      - DATABASE_CONNECTION_CLIENT_NAME=evolution_exchange
      - REDIS_ENABLED=true
      - REDIS_URI=redis://evolution_redis:6379
      - REDIS_PREFIX_KEY=evolution
      - AUTHENTICATION_TYPE=apikey
      - AUTHENTICATION_API_KEY=evolution-api-key-2025
      - AUTHENTICATION_EXPOSE_IN_FETCH_INSTANCES=true
      - WEBHOOK_GLOBAL_ENABLED=false
      - CONFIG_SESSION_PHONE_CLIENT=Evolution API
      - CONFIG_SESSION_PHONE_NAME=Chrome
      - QRCODE_LIMIT=30
      - TYPEBOT_ENABLED=false
      - CHATWOOT_ENABLED=false
      - OPENAI_ENABLED=false
      - DIFY_ENABLED=false
      - WEBSOCKET_ENABLED=false
      - RABBITMQ_ENABLED=false
      - SQS_ENABLED=false
      - S3_ENABLED=false
    depends_on:
      - evolution_postgres
      - evolution_redis
    restart: unless-stopped
```

### Configurações Importantes
- **URL da API**: `http://localhost:8080`
- **API Key**: `evolution-api-key-2025`
- **Porta**: `8080`
- **Interface Web**: `http://localhost:8080`

## 🚀 Como Usar

### 1. Iniciar os Serviços

```bash
# Navegar para o diretório do projeto
cd "DISPARADOR DE MENSAGENS EM LOTE WHATSAPP"

# Iniciar todos os serviços
docker-compose up -d

# Verificar se os serviços estão rodando
docker-compose ps
```

### 2. Conectar WhatsApp

1. **Acesse a interface web**: `http://localhost:8080`
2. **Faça login** com a API Key: `evolution-api-key-2025`
3. **Crie uma instância** ou use a existente `whatsapp-sender`
4. **Escaneie o QR Code** com seu WhatsApp
5. **Aguarde a conexão** ser estabelecida

### 3. Testar a API

```bash
# Executar o script de teste
python3 test_evolution_media.py

# Ou usar o guia interativo
python3 evolution_api_guide.py
```

## 💻 Exemplos de Código

### Inicialização

```python
from evolution_api_guide import EvolutionAPI

# Inicializar cliente
api = EvolutionAPI(
    base_url="http://localhost:8080",
    api_key="evolution-api-key-2025"
)

instance_name = "whatsapp-sender"
phone = "5547996083460"  # Seu número de teste
```

### Enviar Texto

```python
result = api.send_text(
    instance_name,
    phone,
    "🤖 Olá! Esta é uma mensagem de teste."
)

if result['success']:
    print("✅ Mensagem enviada com sucesso!")
else:
    print(f"❌ Erro: {result['data']}")
```

### Enviar Imagem

```python
result = api.send_image(
    instance_name,
    phone,
    "https://exemplo.com/imagem.jpg",
    "🖼️ Legenda da imagem"
)
```

### Enviar Vídeo

```python
result = api.send_video(
    instance_name,
    phone,
    "https://exemplo.com/video.mp4",
    "🎥 Legenda do vídeo"
)
```

### Enviar Documento

```python
result = api.send_document(
    instance_name,
    phone,
    "https://exemplo.com/documento.pdf",
    "documento.pdf",
    "📄 Legenda do documento"
)
```

### Enviar Áudio

```python
result = api.send_audio(
    instance_name,
    phone,
    "https://exemplo.com/audio.mp3"
)
```

## 🔄 Migração do WAHA Core

### Comparação de Endpoints

| Função | WAHA Core | Evolution API |
|--------|-----------|---------------|
| Enviar Texto | `/api/sendText` | `/message/sendText/{instance}` |
| Enviar Imagem | `/api/sendImage` | `/message/sendMedia/{instance}` |
| Enviar Vídeo | `/api/sendVideo` | `/message/sendMedia/{instance}` |
| Enviar Documento | `/api/sendDocument` | `/message/sendMedia/{instance}` |
| Status da Sessão | `/api/sessions/{session}` | `/instance/connectionState/{instance}` |

### Principais Diferenças

1. **Estrutura da URL**: Evolution API usa `{instance}` no final
2. **Mídia unificada**: Todos os tipos de mídia usam `/message/sendMedia`
3. **Autenticação**: API Key no header `apikey`
4. **Formato de resposta**: Estrutura JSON ligeiramente diferente

## 📁 Arquivos do Projeto

- `test_evolution_api.py` - Script básico de teste
- `test_evolution_media.py` - Teste específico de mídia
- `evolution_api_guide.py` - Guia interativo completo
- `docker-compose.yml` - Configuração dos serviços
- `README_EVOLUTION_API.md` - Este guia

## 🛠️ Solução de Problemas

### Problema: QR Code não aparece
**Solução**: 
1. Aguarde alguns segundos após criar a instância
2. Acesse a interface web diretamente
3. Verifique se a instância está no status "connecting"

### Problema: Erro 403 Forbidden
**Solução**: 
1. Verifique se a API Key está correta
2. Confirme se a instância não já existe
3. Delete e recrie a instância se necessário

### Problema: Erro de conexão
**Solução**: 
1. Verifique se o Docker está rodando
2. Confirme se a porta 8080 está disponível
3. Reinicie os serviços: `docker-compose restart`

### Problema: Mensagem não enviada
**Solução**: 
1. Verifique se o WhatsApp está conectado
2. Confirme o formato do número (com código do país)
3. Teste com seu próprio número primeiro

## 🔍 Verificação de Status

```bash
# Verificar logs da Evolution API
docker-compose logs evolution_api

# Verificar status dos containers
docker-compose ps

# Testar conectividade
curl -H "apikey: evolution-api-key-2025" http://localhost:8080/instance/connectionState/whatsapp-sender
```

## 📚 Recursos Adicionais

- [Documentação Oficial](https://github.com/EvolutionAPI/evolution-api)
- [Interface Web](http://localhost:8080)
- [API Reference](https://doc.evolution-api.com/)

## 🎯 Próximos Passos

1. ✅ **Configuração concluída** - Evolution API está rodando
2. 🔄 **Conectar WhatsApp** - Escaneie o QR Code na interface web
3. 🧪 **Testar envios** - Execute os scripts de teste
4. 🔧 **Integrar ao projeto** - Substitua as chamadas do WAHA Core
5. 🚀 **Deploy em produção** - Configure para ambiente de produção

---

**💡 Dica**: A Evolution API oferece todas as funcionalidades do WAHA Core de forma gratuita e com melhor estabilidade. É uma excelente escolha para projetos de automação do WhatsApp!