"""
WhatsApp API Sender - API Communication Module
Módulo responsável pela comunicação com APIs alternativas de WhatsApp
"""

import os
import requests
import logging
import csv
import mimetypes
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class WhatsAppAPISender:
    """
    Classe responsável pelo envio de mensagens via APIs alternativas de WhatsApp
    Suporta diferentes provedores: WAHA, Chat-API, Z-API, UltraMsg, etc.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o sender com as configurações da API
        
        Args:
            config: Dicionário com configurações da API
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.log_filename = f"log_envios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Configurar headers da sessão
        self._setup_session()
        
        # Inicializar arquivo de log
        self._init_log_file()
        
        self.logger.info(f"WhatsApp API Sender inicializado com provider: {config.get('provider', 'unknown')}")
    
    def _setup_session(self):
        """Configura a sessão HTTP com headers padrão"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'WhatsApp-API-Sender/1.0'
        }
        
        # Adicionar token de autenticação conforme o provider
        provider = self.config.get('provider', '').lower()
        token = self.config.get('token', '')
        
        if provider == 'waha':
            headers['X-API-KEY'] = token
        elif provider == 'chat-api':
            headers['Authorization'] = f'Bearer {token}'
        elif provider in ['z-api', 'ultramsg']:
            # Alguns providers usam token na URL ou em headers específicos
            if token:
                headers['X-API-KEY'] = token
        elif provider == 'evolution-api':
            headers['apikey'] = token
        
        self.session.headers.update(headers)
        self.session.timeout = self.config.get('timeout', 30)
    
    def _init_log_file(self):
        """Inicializa o arquivo de log CSV"""
        try:
            with open(self.log_filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['timestamp', 'numero', 'status', 'detalhes', 'provider'])
            self.logger.info(f"Arquivo de log criado: {self.log_filename}")
        except Exception as e:
            self.logger.error(f"Erro ao criar arquivo de log: {e}")
    
    def log_result(self, numero: str, status: str, detalhes: str = ''):
        """
        Registra o resultado de um envio no log
        
        Args:
            numero: Número de telefone
            status: Status do envio (sucesso, erro, etc.)
            detalhes: Detalhes adicionais
        """
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            provider = self.config.get('provider', 'unknown')
            
            with open(self.log_filename, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, numero, status, detalhes, provider])
        except Exception as e:
            self.logger.error(f"Erro ao escrever no log: {e}")
    
    def send_message(self, numero: str, mensagem: str, caminho_midia: str = '') -> bool:
        """
        Envia uma mensagem via API do WhatsApp
        
        Args:
            numero: Número de telefone com DDI (ex: +5521999998888)
            mensagem: Texto da mensagem
            caminho_midia: Caminho para arquivo de mídia (opcional)
            
        Returns:
            bool: True se enviado com sucesso, False caso contrário
        """
        try:
            provider = self.config.get('provider', '').lower()
            
            # Determinar método de envio baseado no provider
            if provider == 'waha':
                return self._send_via_waha(numero, mensagem, caminho_midia)
            elif provider == 'chat-api':
                return self._send_via_chat_api(numero, mensagem, caminho_midia)
            elif provider == 'z-api':
                return self._send_via_z_api(numero, mensagem, caminho_midia)
            elif provider == 'ultramsg':
                return self._send_via_ultramsg(numero, mensagem, caminho_midia)
            elif provider == 'evolution-api':
                return self._send_via_evolution_api(numero, mensagem, caminho_midia)
            else:
                # Provider genérico - tenta usar estrutura padrão
                return self._send_generic(numero, mensagem, caminho_midia)
                
        except Exception as e:
            self.logger.error(f"Erro no envio para {numero}: {e}")
            self.log_result(numero, 'erro', str(e))
            return False
    
    def _send_via_waha(self, numero: str, mensagem: str, caminho_midia: str = '') -> bool:
        """Envia mensagem via API WAHA"""
        base_url = self.config.get('base_url', '')
        instance_id = self.config.get('instance_id', '')
        
        print(f"🔍 [WAHA DEBUG] Iniciando envio para {numero}")
        print(f"🔍 [WAHA DEBUG] Base URL: {base_url}")
        print(f"🔍 [WAHA DEBUG] Instance ID: {instance_id}")
        print(f"🔍 [WAHA DEBUG] Mensagem: {mensagem[:50]}...")
        print(f"🔍 [WAHA DEBUG] Mídia: {caminho_midia if caminho_midia else 'Nenhuma'}")
        
        # Limpar número (remover caracteres especiais)
        numero_limpo = numero.replace('+', '').replace('-', '').replace(' ', '')
        print(f"🔍 [WAHA DEBUG] Número limpo: {numero_limpo}")
        
        try:
            if caminho_midia and os.path.exists(caminho_midia):
                print(f"🔍 [WAHA DEBUG] Enviando mídia: {caminho_midia}")
                # Enviar mídia com caption
                return self._send_media_waha(numero_limpo, mensagem, caminho_midia, base_url, instance_id)
            else:
                print(f"🔍 [WAHA DEBUG] Enviando texto simples")
                # Enviar apenas texto
                url = f"{base_url}/api/sendText"
                print(f"🔍 [WAHA DEBUG] URL completa: {url}")
                
                payload = {
                    "chatId": f"{numero_limpo}@c.us",
                    "text": mensagem,
                    "session": instance_id
                }
                print(f"🔍 [WAHA DEBUG] Payload: {payload}")
                
                print(f"🔍 [WAHA DEBUG] Fazendo requisição POST...")
                response = self.session.post(url, json=payload)
                print(f"🔍 [WAHA DEBUG] Status Code: {response.status_code}")
                print(f"🔍 [WAHA DEBUG] Response Headers: {dict(response.headers)}")
                
                try:
                    response_text = response.text
                    print(f"🔍 [WAHA DEBUG] Response Text: {response_text}")
                except:
                    print(f"🔍 [WAHA DEBUG] Erro ao ler response text")
                
                if response.status_code in [200, 201]:  # 200 OK ou 201 Created
                    try:
                        result = response.json()
                        print(f"🔍 [WAHA DEBUG] Response JSON: {result}")
                        # Para WAHA, se retornou 201 com dados da mensagem, é sucesso
                        if response.status_code == 201 or result.get('success', False):
                            print(f"✅ [WAHA DEBUG] Sucesso no envio!")
                            self.log_result(numero, 'sucesso', 'Mensagem de texto enviada')
                            return True
                        else:
                            error_msg = result.get('message', 'Erro desconhecido')
                            print(f"❌ [WAHA DEBUG] Falha na API: {error_msg}")
                            self.log_result(numero, 'erro', error_msg)
                            return False
                    except Exception as json_error:
                        print(f"❌ [WAHA DEBUG] Erro ao parsear JSON: {json_error}")
                        self.log_result(numero, 'erro', f'Erro JSON: {json_error}')
                        return False
                else:
                    print(f"❌ [WAHA DEBUG] HTTP Error: {response.status_code}")
                    self.log_result(numero, 'erro', f'HTTP {response.status_code}')
                    return False
                    
        except Exception as e:
            print(f"💥 [WAHA DEBUG] Exceção geral: {e}")
            self.logger.error(f"Erro WAHA para {numero}: {e}")
            self.log_result(numero, 'erro', str(e))
            return False
    
    def _send_media_waha(self, numero: str, caption: str, caminho_midia: str, base_url: str, instance_id: str) -> bool:
        """Envia arquivo de mídia via WAHA"""
        try:
            # Determinar tipo de mídia
            mime_type, _ = mimetypes.guess_type(caminho_midia)
            
            if mime_type:
                if mime_type.startswith('image/'):
                    endpoint = "/api/sendImage"
                elif mime_type.startswith('video/'):
                    endpoint = "/api/sendVideo"
                elif mime_type.startswith('audio/'):
                    endpoint = "/api/sendVoice"
                else:
                    endpoint = "/api/sendFile"
            else:
                endpoint = "/api/sendFile"
            
            url = f"{base_url}{endpoint}"
            
            # Preparar arquivos para upload
            with open(caminho_midia, 'rb') as file:
                files = {'file': file}
                data = {
                    'chatId': f"{numero}@c.us",
                    'caption': caption,
                    'session': instance_id
                }
                
                # Enviar sem Content-Type header para upload de arquivo
                headers = self.session.headers.copy()
                if 'Content-Type' in headers:
                    del headers['Content-Type']
                
                response = requests.post(url, files=files, data=data, headers=headers, timeout=60)
                
                if response.status_code in [200, 201]:  # 200 OK ou 201 Created
                    result = response.json()
                    # Para WAHA, se retornou 201 com dados da mensagem, é sucesso
                    if response.status_code == 201 or result.get('success', False):
                        self.log_result(numero, 'sucesso', f'Mídia enviada: {os.path.basename(caminho_midia)}')
                        return True
                    else:
                        error_msg = result.get('message', 'Erro ao enviar mídia')
                        self.log_result(numero, 'erro', error_msg)
                        return False
                else:
                    self.log_result(numero, 'erro', f'HTTP {response.status_code} ao enviar mídia')
                    return False
                    
        except Exception as e:
            self.logger.error(f"Erro ao enviar mídia WAHA para {numero}: {e}")
            self.log_result(numero, 'erro', f'Erro mídia: {str(e)}')
            return False
    
    def _send_via_chat_api(self, numero: str, mensagem: str, caminho_midia: str = '') -> bool:
        """Envia mensagem via Chat-API"""
        base_url = self.config.get('base_url', '')
        instance_id = self.config.get('instance_id', '')
        
        numero_limpo = numero.replace('+', '').replace('-', '').replace(' ', '')
        
        try:
            if caminho_midia and os.path.exists(caminho_midia):
                # Enviar arquivo
                url = f"{base_url}/sendFile"
                
                with open(caminho_midia, 'rb') as file:
                    files = {'file': file}
                    data = {
                        'phone': numero_limpo,
                        'body': mensagem
                    }
                    
                    response = self.session.post(url, files=files, data=data)
            else:
                # Enviar texto
                url = f"{base_url}/sendMessage"
                payload = {
                    "phone": numero_limpo,
                    "body": mensagem
                }
                
                response = self.session.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('sent', False):
                    self.log_result(numero, 'sucesso', 'Mensagem enviada via Chat-API')
                    return True
                else:
                    error_msg = result.get('message', 'Erro Chat-API')
                    self.log_result(numero, 'erro', error_msg)
                    return False
            else:
                self.log_result(numero, 'erro', f'HTTP {response.status_code}')
                return False
                
        except Exception as e:
            self.logger.error(f"Erro Chat-API para {numero}: {e}")
            self.log_result(numero, 'erro', str(e))
            return False
    
    def _send_via_z_api(self, numero: str, mensagem: str, caminho_midia: str = '') -> bool:
        """Envia mensagem via Z-API"""
        base_url = self.config.get('base_url', '')
        instance_id = self.config.get('instance_id', '')
        token = self.config.get('token', '')
        
        numero_limpo = numero.replace('+', '').replace('-', '').replace(' ', '')
        
        try:
            if caminho_midia and os.path.exists(caminho_midia):
                # Para Z-API, geralmente precisa fazer upload primeiro
                url = f"{base_url}/instances/{instance_id}/token/{token}/send-document"
                
                with open(caminho_midia, 'rb') as file:
                    files = {'file': file}
                    data = {
                        'phone': numero_limpo,
                        'message': mensagem
                    }
                    
                    response = self.session.post(url, files=files, data=data)
            else:
                # Enviar texto
                url = f"{base_url}/instances/{instance_id}/token/{token}/send-text"
                payload = {
                    "phone": numero_limpo,
                    "message": mensagem
                }
                
                response = self.session.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success', False):
                    self.log_result(numero, 'sucesso', 'Mensagem enviada via Z-API')
                    return True
                else:
                    error_msg = result.get('error', 'Erro Z-API')
                    self.log_result(numero, 'erro', error_msg)
                    return False
            else:
                self.log_result(numero, 'erro', f'HTTP {response.status_code}')
                return False
                
        except Exception as e:
            self.logger.error(f"Erro Z-API para {numero}: {e}")
            self.log_result(numero, 'erro', str(e))
            return False
    
    def _send_via_ultramsg(self, numero: str, mensagem: str, caminho_midia: str = '') -> bool:
        """Envia mensagem via UltraMsg"""
        base_url = self.config.get('base_url', '')
        token = self.config.get('token', '')
        
        numero_limpo = numero.replace('+', '').replace('-', '').replace(' ', '')
        
        try:
            if caminho_midia and os.path.exists(caminho_midia):
                # Enviar documento
                url = f"{base_url}/messages/document"
                
                with open(caminho_midia, 'rb') as file:
                    files = {'document': file}
                    data = {
                        'token': token,
                        'to': numero_limpo,
                        'caption': mensagem
                    }
                    
                    response = self.session.post(url, files=files, data=data)
            else:
                # Enviar texto
                url = f"{base_url}/messages/chat"
                payload = {
                    "token": token,
                    "to": numero_limpo,
                    "body": mensagem
                }
                
                response = self.session.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('sent', False):
                    self.log_result(numero, 'sucesso', 'Mensagem enviada via UltraMsg')
                    return True
                else:
                    error_msg = result.get('error', 'Erro UltraMsg')
                    self.log_result(numero, 'erro', error_msg)
                    return False
            else:
                self.log_result(numero, 'erro', f'HTTP {response.status_code}')
                return False
                
        except Exception as e:
            self.logger.error(f"Erro UltraMsg para {numero}: {e}")
            self.log_result(numero, 'erro', str(e))
            return False
    
    def _send_generic(self, numero: str, mensagem: str, caminho_midia: str = '') -> bool:
        """Envio genérico para APIs não específicas"""
        base_url = self.config.get('base_url', '')
        
        numero_limpo = numero.replace('+', '').replace('-', '').replace(' ', '')
        
        try:
            if caminho_midia and os.path.exists(caminho_midia):
                # Tentar envio de arquivo genérico
                endpoint = self.config.get('media_endpoint', '/send-media')
                url = f"{base_url}{endpoint}"
                
                with open(caminho_midia, 'rb') as file:
                    files = {'file': file}
                    data = {
                        'phone': numero_limpo,
                        'message': mensagem
                    }
                    
                    response = self.session.post(url, files=files, data=data)
            else:
                # Envio de texto genérico
                endpoint = self.config.get('text_endpoint', '/send-message')
                url = f"{base_url}{endpoint}"
                payload = {
                    "phone": numero_limpo,
                    "message": mensagem
                }
                
                response = self.session.post(url, json=payload)
            
            if response.status_code == 200:
                self.log_result(numero, 'sucesso', 'Mensagem enviada (genérico)')
                return True
            else:
                self.log_result(numero, 'erro', f'HTTP {response.status_code}')
                return False
                
        except Exception as e:
            self.logger.error(f"Erro genérico para {numero}: {e}")
            self.log_result(numero, 'erro', str(e))
            return False
    
    def _send_via_evolution_api(self, numero: str, mensagem: str, caminho_midia: str = '') -> bool:
        """Envia mensagem via Evolution API"""
        base_url = self.config.get('base_url', '')
        instance_id = self.config.get('instance_id', '')
        
        print(f"🔍 [EVOLUTION DEBUG] Iniciando envio para {numero}")
        print(f"🔍 [EVOLUTION DEBUG] Base URL: {base_url}")
        print(f"🔍 [EVOLUTION DEBUG] Instance ID: {instance_id}")
        print(f"🔍 [EVOLUTION DEBUG] Mensagem: {mensagem[:50]}...")
        print(f"🔍 [EVOLUTION DEBUG] Mídia: {caminho_midia if caminho_midia else 'Nenhuma'}")
        
        # Limpar número (remover caracteres especiais)
        numero_limpo = numero.replace('+', '').replace('-', '').replace(' ', '')
        print(f"🔍 [EVOLUTION DEBUG] Número limpo: {numero_limpo}")
        
        try:
            if caminho_midia and os.path.exists(caminho_midia):
                print(f"🔍 [EVOLUTION DEBUG] Enviando mídia: {caminho_midia}")
                # Enviar mídia com caption
                return self._send_media_evolution_api(numero_limpo, mensagem, caminho_midia, base_url, instance_id)
            else:
                print(f"🔍 [EVOLUTION DEBUG] Enviando texto simples")
                # Enviar apenas texto
                url = f"{base_url}/message/sendText/{instance_id}"
                print(f"🔍 [EVOLUTION DEBUG] URL completa: {url}")
                
                payload = {
                    "number": numero_limpo,
                    "text": mensagem
                }
                print(f"🔍 [EVOLUTION DEBUG] Payload: {payload}")
                
                print(f"🔍 [EVOLUTION DEBUG] Fazendo requisição POST...")
                response = self.session.post(url, json=payload)
                print(f"🔍 [EVOLUTION DEBUG] Status Code: {response.status_code}")
                print(f"🔍 [EVOLUTION DEBUG] Response Headers: {dict(response.headers)}")
                
                try:
                    response_text = response.text
                    print(f"🔍 [EVOLUTION DEBUG] Response Text: {response_text}")
                except:
                    print(f"🔍 [EVOLUTION DEBUG] Erro ao ler response text")
                
                if response.status_code in [200, 201]:  # 200 OK ou 201 Created
                    try:
                        result = response.json()
                        print(f"🔍 [EVOLUTION DEBUG] Response JSON: {result}")
                        # Para Evolution API, verificar se há key no resultado
                        if result.get('key') or result.get('messageId'):
                            print(f"✅ [EVOLUTION DEBUG] Sucesso no envio!")
                            self.log_result(numero, 'sucesso', 'Mensagem de texto enviada')
                            return True
                        else:
                            error_msg = result.get('message', 'Erro desconhecido')
                            print(f"❌ [EVOLUTION DEBUG] Falha na API: {error_msg}")
                            self.log_result(numero, 'erro', error_msg)
                            return False
                    except Exception as json_error:
                        print(f"❌ [EVOLUTION DEBUG] Erro ao parsear JSON: {json_error}")
                        self.log_result(numero, 'erro', f'Erro JSON: {json_error}')
                        return False
                else:
                    print(f"❌ [EVOLUTION DEBUG] HTTP Error: {response.status_code}")
                    self.log_result(numero, 'erro', f'HTTP {response.status_code}')
                    return False
                    
        except Exception as e:
            print(f"💥 [EVOLUTION DEBUG] Exceção geral: {e}")
            self.logger.error(f"Erro Evolution API para {numero}: {e}")
            self.log_result(numero, 'erro', str(e))
            return False
    
    def _send_media_evolution_api(self, numero: str, caption: str, caminho_midia: str, base_url: str, instance_id: str) -> bool:
        """Envia arquivo de mídia via Evolution API com retry logic avançado"""
        max_tentativas = 3
        timeouts = [30, 60, 120]  # Timeouts progressivos
        
        # Validações iniciais
        if not os.path.exists(caminho_midia):
            self.log_result(numero, 'erro', f'Arquivo não encontrado: {caminho_midia}')
            return False
        
        # Verificar tamanho do arquivo
        tamanho_mb = os.path.getsize(caminho_midia) / (1024 * 1024)
        if tamanho_mb > 64:  # Limite amplo para Evolution API
            self.log_result(numero, 'erro', f'Arquivo muito grande: {tamanho_mb:.1f}MB (máximo 64MB)')
            return False
        
        for tentativa in range(max_tentativas):
            try:
                print(f"🔄 [MÍDIA] Tentativa {tentativa + 1}/{max_tentativas} para {os.path.basename(caminho_midia)}")
                
                # Determinar tipo de mídia e endpoint
                mime_type, _ = mimetypes.guess_type(caminho_midia)
                endpoint, media_type = self._get_evolution_endpoint_and_type(mime_type)
                
                url = f"{base_url}{endpoint.format(instance_id=instance_id)}"
                print(f"🔗 [MÍDIA] URL: {url}")
                print(f"📎 [MÍDIA] Tipo: {media_type} | Tamanho: {tamanho_mb:.1f}MB")
                
                # Preparar dados para upload
                with open(caminho_midia, 'rb') as file:
                    files = {'attachment': file}
                    data = {
                        'number': numero,
                        'caption': caption,
                        'mediatype': media_type
                    }
                    
                    # Headers otimizados para upload
                    headers = self.session.headers.copy()
                    if 'Content-Type' in headers:
                        del headers['Content-Type']
                    
                    timeout = timeouts[min(tentativa, len(timeouts) - 1)]
                    print(f"⏱️  [MÍDIA] Timeout: {timeout}s")
                    
                    response = requests.post(url, files=files, data=data, 
                                           headers=headers, timeout=timeout)
                    
                    print(f"📡 [MÍDIA] Status: {response.status_code}")
                    
                    # Verificar resposta
                    if response.status_code in [200, 201]:
                        try:
                            result = response.json()
                            print(f"📋 [MÍDIA] Resposta: {result}")
                            
                            # Verificar sucesso da Evolution API
                            if result.get('key') or result.get('messageId') or result.get('id'):
                                print(f"✅ [MÍDIA] Mídia enviada com sucesso!")
                                self.log_result(numero, 'sucesso', 
                                              f'Mídia enviada: {os.path.basename(caminho_midia)} ({tamanho_mb:.1f}MB)')
                                return True
                            else:
                                error_msg = result.get('message', 'Resposta sem ID válido')
                                print(f"⚠️  [MÍDIA] Falha na API: {error_msg}")
                                
                                if tentativa < max_tentativas - 1:
                                    print(f"🔄 [MÍDIA] Tentando novamente em 3s...")
                                    import time
                                    time.sleep(3)
                                    continue
                                else:
                                    self.log_result(numero, 'erro', error_msg)
                                    return False
                                    
                        except json.JSONDecodeError as json_error:
                            print(f"⚠️  [MÍDIA] Erro JSON: {json_error}")
                            if tentativa < max_tentativas - 1:
                                print(f"🔄 [MÍDIA] Tentando novamente...")
                                import time
                                time.sleep(2)
                                continue
                            else:
                                self.log_result(numero, 'erro', f'Erro JSON: {json_error}')
                                return False
                    
                    elif response.status_code == 401:
                        print(f"🔐 [MÍDIA] Erro de autenticação (401)")
                        self.log_result(numero, 'erro', 'Token de API inválido')
                        return False  # Não tentar novamente para erro de auth
                    
                    elif response.status_code == 413:
                        print(f"📏 [MÍDIA] Arquivo muito grande (413)")
                        self.log_result(numero, 'erro', 'Arquivo excede limite do servidor')
                        return False  # Não tentar novamente para arquivo grande
                    
                    elif response.status_code in [500, 502, 503, 504]:
                        print(f"🔧 [MÍDIA] Erro do servidor ({response.status_code})")
                        if tentativa < max_tentativas - 1:
                            wait_time = (tentativa + 1) * 5  # 5s, 10s, 15s
                            print(f"⏳ [MÍDIA] Aguardando {wait_time}s antes de tentar novamente...")
                            import time
                            time.sleep(wait_time)
                            continue
                        else:
                            self.log_result(numero, 'erro', f'Erro servidor: HTTP {response.status_code}')
                            return False
                    
                    else:
                        print(f"❌ [MÍDIA] HTTP {response.status_code}")
                        if tentativa < max_tentativas - 1:
                            print(f"🔄 [MÍDIA] Tentando novamente...")
                            import time
                            time.sleep(2)
                            continue
                        else:
                            self.log_result(numero, 'erro', f'HTTP {response.status_code}')
                            return False
                            
            except requests.exceptions.Timeout:
                print(f"⏰ [MÍDIA] Timeout na tentativa {tentativa + 1}")
                if tentativa < max_tentativas - 1:
                    print(f"🔄 [MÍDIA] Aumentando timeout e tentando novamente...")
                    continue
                else:
                    self.log_result(numero, 'erro', f'Timeout após {max_tentativas} tentativas')
                    return False
                    
            except requests.exceptions.ConnectionError:
                print(f"🔌 [MÍDIA] Erro de conexão na tentativa {tentativa + 1}")
                if tentativa < max_tentativas - 1:
                    print(f"🔄 [MÍDIA] Tentando reconectar...")
                    import time
                    time.sleep(5)
                    continue
                else:
                    self.log_result(numero, 'erro', 'Erro de conexão persistente')
                    return False
                    
            except Exception as e:
                print(f"💥 [MÍDIA] Erro inesperado: {e}")
                if tentativa < max_tentativas - 1:
                    print(f"🔄 [MÍDIA] Tentando novamente...")
                    import time
                    time.sleep(2)
                    continue
                else:
                    self.logger.error(f"Erro ao enviar mídia Evolution API para {numero}: {e}")
                    self.log_result(numero, 'erro', f'Erro: {str(e)}')
                    return False
        
        return False
    
    def _get_evolution_endpoint_and_type(self, mime_type: str) -> tuple:
        """Determina endpoint e tipo de mídia para Evolution API"""
        if not mime_type:
            return "/message/sendMedia/{instance_id}", "document"
        
        if mime_type.startswith('image/'):
            return "/message/sendMedia/{instance_id}", "image"
        elif mime_type.startswith('video/'):
            return "/message/sendMedia/{instance_id}", "video"
        elif mime_type.startswith('audio/'):
            return "/message/sendWhatsAppAudio/{instance_id}", "audio"
        else:
            return "/message/sendMedia/{instance_id}", "document"
    
    def get_log_filename(self) -> str:
        """Retorna o nome do arquivo de log"""
        return self.log_filename