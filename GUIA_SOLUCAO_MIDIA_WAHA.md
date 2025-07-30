# Guia Completo: Soluções para Problemas de Envio de Mídia no WAHA

## 📋 Problemas Identificados nos Logs

Analisando os logs do sistema, foram identificados os seguintes erros recorrentes:

- **HTTP 401**: Erro de autenticação (token inválido ou expirado)
- **HTTP 422**: Dados inválidos ou formato não suportado
- **HTTP 500**: Erro interno do servidor WAHA

## 🔍 Principais Causas e Soluções

### 1. Erro HTTP 401 - Unauthorized

**Causa**: Token de API inválido ou expirado

**Soluções**:
```bash
# Verificar se o WAHA está rodando
curl -X GET "http://localhost:3000/api/sessions" \
  -H "X-API-KEY: sua-chave-aqui"

# Verificar status da sessão
curl -X GET "http://localhost:3000/api/sessions/default" \
  -H "X-API-KEY: sua-chave-aqui"
```

**Configuração correta no config.json**:
```json
{
  "provider": "waha",
  "base_url": "http://localhost:3000",
  "token": "sua-chave-api-valida",
  "instance_id": "default"
}
```

### 2. Erro HTTP 422 - Unprocessable Entity

**Causa**: Formato de arquivo não suportado ou dados inválidos

**Formatos suportados pelo WhatsApp**:
- **Imagens**: JPG, JPEG, PNG, GIF, WEBP
- **Vídeos**: MP4 (codec H.264)
- **Áudios**: MP3, OGG, AAC, M4A
- **Documentos**: PDF, DOC, DOCX, XLS, XLSX, TXT

**Limites de tamanho**:
- Imagens: até 5MB
- Vídeos: até 16MB
- Áudios: até 16MB
- Documentos: até 100MB

### 3. Erro HTTP 500 - Internal Server Error

**Causa**: Problemas internos do WAHA (sessão desconectada, motor WEBJS com limitações)

**Soluções**:

#### A. Usar WAHA Plus (Recomendado)
```bash
# Docker Compose para WAHA Plus
version: '3.8'
services:
  waha:
    image: devlikeapro/waha-plus:chrome
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - WAHA_API_KEY=sua-chave-segura
      - WAHA_PRINT_QR=false
    volumes:
      - waha_files:/app/files

volumes:
  waha_files:
```

#### B. Verificar Status da Sessão
```python
import requests

def verificar_sessao_waha():
    url = "http://localhost:3000/api/sessions/default"
    headers = {"X-API-KEY": "sua-chave"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {data.get('status')}")
        return data.get('status') == 'WORKING'
    return False
```

#### C. Reiniciar Sessão se Necessário
```python
def reiniciar_sessao_waha():
    base_url = "http://localhost:3000"
    headers = {"X-API-KEY": "sua-chave"}
    
    # Parar sessão
    requests.post(f"{base_url}/api/sessions/default/stop", headers=headers)
    
    # Iniciar nova sessão
    payload = {
        "name": "default",
        "config": {
            "proxy": None,
            "webhooks": []
        }
    }
    response = requests.post(f"{base_url}/api/sessions/start", 
                           json=payload, headers=headers)
    return response.status_code == 201
```

## 🛠️ Implementação de Retry Logic

### Melhorar o método _send_media_waha

```python
def _send_media_waha_melhorado(self, numero: str, caption: str, caminho_midia: str, base_url: str, instance_id: str) -> bool:
    """Envia arquivo de mídia via WAHA com retry logic"""
    max_tentativas = 3
    
    for tentativa in range(max_tentativas):
        try:
            # Verificar se arquivo existe e é válido
            if not os.path.exists(caminho_midia):
                self.log_result(numero, 'erro', f'Arquivo não encontrado: {caminho_midia}')
                return False
            
            # Verificar tamanho do arquivo
            tamanho_mb = os.path.getsize(caminho_midia) / (1024 * 1024)
            if tamanho_mb > 16:  # Limite do WhatsApp
                self.log_result(numero, 'erro', f'Arquivo muito grande: {tamanho_mb:.1f}MB')
                return False
            
            # Determinar tipo de mídia e endpoint
            mime_type, _ = mimetypes.guess_type(caminho_midia)
            endpoint = self._get_endpoint_by_mime_type(mime_type)
            
            url = f"{base_url}{endpoint}"
            
            # Preparar dados para envio
            with open(caminho_midia, 'rb') as file:
                files = {'file': file}
                data = {
                    'chatId': f"{numero}@c.us",
                    'caption': caption,
                    'session': instance_id
                }
                
                # Headers sem Content-Type para multipart
                headers = self.session.headers.copy()
                if 'Content-Type' in headers:
                    del headers['Content-Type']
                
                response = requests.post(url, files=files, data=data, 
                                       headers=headers, timeout=60)
                
                # Verificar resposta
                if response.status_code in [200, 201]:
                    try:
                        result = response.json()
                        if response.status_code == 201 or result.get('success', False):
                            self.log_result(numero, 'sucesso', 
                                          f'Mídia enviada: {os.path.basename(caminho_midia)}')
                            return True
                        else:
                            error_msg = result.get('message', 'Erro desconhecido')
                            if tentativa < max_tentativas - 1:
                                print(f"Tentativa {tentativa + 1} falhou: {error_msg}. Tentando novamente...")
                                time.sleep(2)  # Aguardar antes de tentar novamente
                                continue
                            else:
                                self.log_result(numero, 'erro', error_msg)
                                return False
                    except json.JSONDecodeError:
                        if tentativa < max_tentativas - 1:
                            print(f"Erro ao decodificar JSON na tentativa {tentativa + 1}")
                            time.sleep(2)
                            continue
                        else:
                            self.log_result(numero, 'erro', 'Resposta inválida do servidor')
                            return False
                
                elif response.status_code == 401:
                    self.log_result(numero, 'erro', 'Token de API inválido ou expirado')
                    return False  # Não tentar novamente para erro de autenticação
                
                elif response.status_code == 422:
                    self.log_result(numero, 'erro', 'Formato de arquivo não suportado')
                    return False  # Não tentar novamente para formato inválido
                
                elif response.status_code == 500:
                    if tentativa < max_tentativas - 1:
                        print(f"Erro 500 na tentativa {tentativa + 1}. Verificando sessão...")
                        # Verificar e reiniciar sessão se necessário
                        if not self._verificar_sessao_ativa(base_url, instance_id):
                            self._reiniciar_sessao(base_url, instance_id)
                        time.sleep(5)  # Aguardar mais tempo para erro 500
                        continue
                    else:
                        self.log_result(numero, 'erro', 'Erro interno do servidor WAHA')
                        return False
                
                else:
                    if tentativa < max_tentativas - 1:
                        print(f"HTTP {response.status_code} na tentativa {tentativa + 1}")
                        time.sleep(2)
                        continue
                    else:
                        self.log_result(numero, 'erro', f'HTTP {response.status_code}')
                        return False
                        
        except Exception as e:
            if tentativa < max_tentativas - 1:
                print(f"Exceção na tentativa {tentativa + 1}: {e}")
                time.sleep(2)
                continue
            else:
                self.logger.error(f"Erro ao enviar mídia WAHA para {numero}: {e}")
                self.log_result(numero, 'erro', f'Erro: {str(e)}')
                return False
    
    return False

def _get_endpoint_by_mime_type(self, mime_type: str) -> str:
    """Determina o endpoint correto baseado no tipo MIME"""
    if not mime_type:
        return "/api/sendFile"
    
    if mime_type.startswith('image/'):
        return "/api/sendImage"
    elif mime_type.startswith('video/'):
        return "/api/sendVideo"
    elif mime_type.startswith('audio/'):
        return "/api/sendVoice"
    else:
        return "/api/sendFile"

def _verificar_sessao_ativa(self, base_url: str, instance_id: str) -> bool:
    """Verifica se a sessão WAHA está ativa"""
    try:
        url = f"{base_url}/api/sessions/{instance_id}"
        response = self.session.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('status') == 'WORKING'
    except:
        pass
    return False

def _reiniciar_sessao(self, base_url: str, instance_id: str) -> bool:
    """Reinicia a sessão WAHA"""
    try:
        # Parar sessão atual
        stop_url = f"{base_url}/api/sessions/{instance_id}/stop"
        self.session.post(stop_url, timeout=10)
        
        time.sleep(3)  # Aguardar parada completa
        
        # Iniciar nova sessão
        start_url = f"{base_url}/api/sessions/start"
        payload = {
            "name": instance_id,
            "config": {
                "proxy": None,
                "webhooks": []
            }
        }
        response = self.session.post(start_url, json=payload, timeout=30)
        return response.status_code == 201
    except:
        return False
```

## 🔧 Configurações Recomendadas

### Docker Compose Otimizado
```yaml
version: '3.8'
services:
  waha:
    image: devlikeapro/waha-plus:chrome
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - WAHA_API_KEY=sua-chave-muito-segura
      - WAHA_PRINT_QR=false
      - WAHA_LOG_LEVEL=info
    volumes:
      - waha_files:/app/files
      - waha_sessions:/app/.sessions
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  waha_files:
  waha_sessions:
```

### Configuração do Sistema
```json
{
  "provider": "waha",
  "base_url": "http://localhost:3000",
  "token": "sua-chave-api-segura",
  "instance_id": "default",
  "timeout": 60,
  "max_retries": 3,
  "retry_delay": 2
}
```

## 🚀 Alternativa: Evolution API

Se os problemas persistirem com o WAHA, considere migrar para a Evolution API:

```bash
# Instalar Evolution API
git clone https://github.com/EvolutionAPI/evolution-api.git
cd evolution-api
docker-compose up -d
```

**Vantagens da Evolution API**:
- Melhor suporte para envio de mídia
- Mais estável para operações em lote
- Documentação mais completa
- Suporte ativo da comunidade

## 📝 Checklist de Verificação

- [ ] WAHA Plus está rodando (não o Core gratuito)
- [ ] Token de API está correto e válido
- [ ] Sessão WhatsApp está conectada (status: WORKING)
- [ ] Arquivos de mídia estão no formato correto
- [ ] Tamanho dos arquivos está dentro dos limites
- [ ] Retry logic implementado no código
- [ ] Logs detalhados habilitados para debug

## 🔍 Debug e Monitoramento

```python
# Script para monitorar status do WAHA
import requests
import time

def monitorar_waha():
    base_url = "http://localhost:3000"
    headers = {"X-API-KEY": "sua-chave"}
    
    while True:
        try:
            response = requests.get(f"{base_url}/api/sessions", headers=headers)
            if response.status_code == 200:
                sessions = response.json()
                for session in sessions:
                    print(f"Sessão {session['name']}: {session['status']}")
            else:
                print(f"Erro ao verificar sessões: {response.status_code}")
        except Exception as e:
            print(f"Erro de conexão: {e}")
        
        time.sleep(30)  # Verificar a cada 30 segundos

if __name__ == "__main__":
    monitorar_waha()
```

## 📞 Suporte

Se os problemas persistirem:
1. Verifique os logs do Docker: `docker logs container_waha`
2. Teste com arquivos pequenos primeiro
3. Considere usar a Evolution API como alternativa
4. Consulte a documentação oficial do WAHA

---

**Nota**: Este guia foi criado baseado na análise dos logs do sistema e nas melhores práticas para integração com APIs do WhatsApp.