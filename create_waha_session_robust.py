#!/usr/bin/env python3
"""
Script robusto para criar sessão WAHA com tratamento de erros aprimorado
"""

import requests
import json
import time
from datetime import datetime

def create_waha_session_robust():
    """Cria uma sessão WAHA de forma robusta com tratamento de erros"""
    
    # Configurações
    base_url = "http://localhost:3000"
    api_key = "waha-key-2025"  # Chave de API do projeto
    session_name = "default"
    
    print("🔧 Criação Robusta da Sessão WAHA")
    print("=" * 45)
    
    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': api_key
    }
    
    # Passo 1: Verificar conectividade
    print("\n1️⃣ Verificando conectividade...")
    if not test_connectivity(base_url, headers):
        return False
    
    # Passo 2: Limpar sessões existentes
    print("\n2️⃣ Limpando sessões existentes...")
    clean_existing_sessions(base_url, headers)
    
    # Passo 3: Criar nova sessão
    print("\n3️⃣ Criando nova sessão...")
    if create_new_session(base_url, headers, session_name):
        print("\n4️⃣ Monitorando inicialização...")
        return monitor_session(base_url, headers, session_name)
    
    return False

def test_connectivity(base_url, headers):
    """Testa conectividade com o servidor WAHA"""
    try:
        # Testar endpoint de versão (não requer autenticação)
        response = requests.get(f"{base_url}/api/version", timeout=10)
        
        if response.status_code == 200:
            try:
                version_data = response.json()
                print(f"   ✅ Servidor WAHA ativo - Versão: {version_data.get('version')}")
            except:
                print("   ✅ Servidor WAHA ativo")
        elif response.status_code == 401:
            print("   ✅ Servidor ativo (requer autenticação)")
        else:
            print(f"   ⚠️ Servidor respondeu com status: {response.status_code}")
        
        # Testar autenticação
        auth_response = requests.get(f"{base_url}/api/sessions", headers=headers, timeout=10)
        
        if auth_response.status_code == 200:
            print("   ✅ Autenticação válida")
            return True
        elif auth_response.status_code == 401:
            print("   ❌ Falha na autenticação - verifique a API key")
            return False
        else:
            print(f"   ⚠️ Status de autenticação: {auth_response.status_code}")
            return True  # Continuar mesmo com status inesperado
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Não foi possível conectar ao servidor WAHA")
        print("   💡 Verifique se o servidor está rodando na porta 3000")
        return False
    except Exception as e:
        print(f"   ❌ Erro de conectividade: {e}")
        return False

def clean_existing_sessions(base_url, headers):
    """Limpa todas as sessões existentes"""
    try:
        response = requests.get(f"{base_url}/api/sessions", headers=headers, timeout=10)
        
        if response.status_code == 200:
            try:
                sessions = response.json()
                print(f"   📋 Encontradas {len(sessions)} sessões")
                
                for session in sessions:
                    name = session.get('name', 'unknown')
                    status = session.get('status', 'unknown')
                    print(f"   🗑️ Deletando sessão: {name} (status: {status})")
                    
                    try:
                        delete_response = requests.delete(f"{base_url}/api/sessions/{name}", 
                                                        headers=headers, timeout=10)
                        
                        if delete_response.status_code in [200, 404]:
                            print(f"   ✅ Sessão {name} deletada")
                        else:
                            print(f"   ⚠️ Status ao deletar {name}: {delete_response.status_code}")
                            
                    except Exception as e:
                        print(f"   ❌ Erro ao deletar {name}: {e}")
                        
            except json.JSONDecodeError:
                print("   ⚠️ Resposta inválida ao listar sessões")
                print(f"   Resposta raw: {response.text[:200]}")
        else:
            print(f"   ⚠️ Status ao listar sessões: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro ao limpar sessões: {e}")
    
    # Aguardar um pouco após limpeza
    time.sleep(2)

def create_new_session(base_url, headers, session_name):
    """Cria uma nova sessão com configuração simples"""
    try:
        # Configuração mínima para evitar problemas
        payload = {
            "name": session_name
        }
        
        print(f"   📤 Enviando requisição para criar sessão '{session_name}'...")
        print(f"   🔗 URL: {base_url}/api/sessions")
        print(f"   📋 Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(f"{base_url}/api/sessions", 
                               json=payload, 
                               headers=headers, 
                               timeout=15)
        
        print(f"   📊 Status da resposta: {response.status_code}")
        print(f"   📄 Headers da resposta: {dict(response.headers)}")
        
        # Tentar processar a resposta
        response_text = response.text
        print(f"   📝 Resposta raw: {response_text[:500]}")
        
        if response.status_code in [200, 201]:
            try:
                session_data = response.json()
                print("   ✅ Sessão criada com sucesso")
                print(f"   📊 Dados da sessão: {json.dumps(session_data, indent=2)}")
                return True
            except json.JSONDecodeError:
                print("   ⚠️ Sessão criada, mas resposta não é JSON válido")
                # Verificar se a sessão foi realmente criada
                time.sleep(2)
                return verify_session_exists(base_url, headers, session_name)
        elif response.status_code == 422:
            print("   ⚠️ Sessão pode já existir ou parâmetros inválidos")
            try:
                error_data = response.json()
                print(f"   Detalhes do erro: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Resposta de erro: {response_text}")
            
            # Verificar se a sessão existe
            return verify_session_exists(base_url, headers, session_name)
        else:
            print(f"   ❌ Erro ao criar sessão: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Detalhes: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Resposta: {response_text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro na criação da sessão: {e}")
        return False

def verify_session_exists(base_url, headers, session_name):
    """Verifica se a sessão existe"""
    try:
        print(f"   🔍 Verificando se sessão '{session_name}' existe...")
        response = requests.get(f"{base_url}/api/sessions/{session_name}", 
                              headers=headers, timeout=10)
        
        if response.status_code == 200:
            try:
                session_data = response.json()
                status = session_data.get('status', 'unknown')
                print(f"   ✅ Sessão encontrada com status: {status}")
                return True
            except:
                print("   ✅ Sessão encontrada (resposta não-JSON)")
                return True
        elif response.status_code == 404:
            print("   ❌ Sessão não encontrada")
            return False
        else:
            print(f"   ⚠️ Status inesperado ao verificar sessão: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro ao verificar sessão: {e}")
        return False

def monitor_session(base_url, headers, session_name):
    """Monitora o status da sessão"""
    print(f"   🔄 Monitorando sessão '{session_name}'...")
    
    max_attempts = 20
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(f"{base_url}/api/sessions/{session_name}", 
                                  headers=headers, timeout=10)
            
            if response.status_code == 200:
                try:
                    session_data = response.json()
                    status = session_data.get('status', 'unknown')
                    
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"   [{timestamp}] Status: {status}")
                    
                    if status == 'STARTING':
                        if attempt == 0:
                            print("   📱 QR Code disponível em: http://127.0.0.1:5000/qr_waha")
                            print("   📲 Escaneie o QR code com seu WhatsApp")
                        print("   ⏳ Aguardando escaneamento...")
                    elif status == 'WORKING':
                        me = session_data.get('me')
                        if me:
                            print(f"   ✅ Conectado como: {me.get('pushname')} ({me.get('id')})")
                        print("   🎉 Sessão funcionando perfeitamente!")
                        return True
                    elif status == 'FAILED':
                        print("   ❌ Sessão falhou")
                        return False
                    else:
                        print(f"   ⚠️ Status: {status}")
                        
                except json.JSONDecodeError:
                    print(f"   ⚠️ Resposta inválida: {response.text[:100]}")
            else:
                print(f"   ❌ Erro ao verificar status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erro no monitoramento: {e}")
            return False
        
        attempt += 1
        time.sleep(5)  # Aguardar 5 segundos entre verificações
    
    print("   ⏰ Timeout no monitoramento")
    return False

if __name__ == "__main__":
    print("🚀 Iniciando criação robusta da sessão WAHA...")
    
    success = create_waha_session_robust()
    
    print("\n" + "=" * 45)
    if success:
        print("🎉 Sessão WAHA criada e funcionando com sucesso!")
    else:
        print("❌ Falha na criação da sessão WAHA")
        print("💡 Verifique se o servidor WAHA está rodando corretamente")
    
    print("🏁 Processo finalizado")