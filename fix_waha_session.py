#!/usr/bin/env python3
"""
Script para corrigir problemas específicos da sessão WAHA
"""

import requests
import json
import time
from datetime import datetime

def fix_waha_session():
    """Corrige problemas específicos da sessão WAHA"""
    
    # Configurações WAHA
    base_url = "http://localhost:3000"
    api_key = "waha-key-2025"
    session_name = "default"
    
    print("🔧 Correção da Sessão WAHA")
    print("=" * 40)
    
    headers = {'X-Api-Key': api_key}
    
    # Passo 1: Verificar sessões existentes
    print("\n1️⃣ Verificando sessões existentes...")
    try:
        response = requests.get(f"{base_url}/api/sessions", headers=headers, timeout=10)
        if response.status_code == 200:
            sessions = response.json()
            print(f"   📋 Sessões encontradas: {len(sessions)}")
            
            for session in sessions:
                name = session.get('name')
                status = session.get('status')
                print(f"   - {name}: {status}")
                
                # Se encontrar uma sessão com problema, deletar
                if status in ['STARTING', 'FAILED', 'STOPPED']:
                    print(f"   🗑️ Deletando sessão problemática: {name}")
                    delete_response = requests.delete(f"{base_url}/api/sessions/{name}", headers=headers)
                    if delete_response.status_code in [200, 404]:
                        print(f"   ✅ Sessão {name} deletada")
                    else:
                        print(f"   ❌ Erro ao deletar {name}: {delete_response.status_code}")
        else:
            print(f"   ❌ Erro ao listar sessões: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Aguardar um pouco
    time.sleep(3)
    
    # Passo 2: Criar nova sessão com configuração específica
    print("\n2️⃣ Criando nova sessão com configuração otimizada...")
    try:
        # Configuração otimizada para WEBJS
        payload = {
            "name": session_name,
            "config": {
                "proxy": None,
                "webhooks": [],
                "debug": False,
                "noweb": {
                    "store": {
                        "enabled": True,
                        "fullSync": False
                    }
                }
            }
        }
        
        response = requests.post(f"{base_url}/api/sessions", 
                               json=payload, headers=headers, timeout=15)
        
        if response.status_code in [200, 201]:
            session_data = response.json()
            print("   ✅ Nova sessão criada com sucesso")
            print(f"   📊 Status: {session_data.get('status')}")
            
            # Aguardar a sessão se estabilizar
            print("   ⏳ Aguardando estabilização da sessão...")
            time.sleep(5)
            
            # Verificar status da nova sessão
            status_response = requests.get(f"{base_url}/api/sessions/{session_name}", headers=headers)
            if status_response.status_code == 200:
                status_data = status_response.json()
                current_status = status_data.get('status')
                print(f"   📊 Status atual: {current_status}")
                
                if current_status == 'STARTING':
                    print("   ✅ Sessão está iniciando corretamente")
                    return True
                elif current_status == 'WORKING':
                    print("   ✅ Sessão já está funcionando!")
                    return True
                else:
                    print(f"   ⚠️ Status inesperado: {current_status}")
                    return False
            else:
                print(f"   ❌ Erro ao verificar status: {status_response.status_code}")
                return False
        else:
            print(f"   ❌ Erro ao criar sessão: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Detalhes: {error_data}")
            except:
                print(f"   Resposta: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def monitor_session_startup():
    """Monitora o processo de inicialização da sessão"""
    
    base_url = "http://localhost:3000"
    api_key = "waha-key-2025"
    session_name = "default"
    headers = {'X-Api-Key': api_key}
    
    print("\n3️⃣ Monitorando inicialização da sessão...")
    
    max_attempts = 30  # 30 tentativas (5 minutos)
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(f"{base_url}/api/sessions/{session_name}", headers=headers, timeout=10)
            
            if response.status_code == 200:
                session_data = response.json()
                status = session_data.get('status')
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"   [{timestamp}] Status: {status}")
                
                if status == 'WORKING':
                    me = session_data.get('me')
                    if me:
                        print(f"   ✅ Conectado como: {me.get('pushname')} ({me.get('id')})")
                    print("   🎉 Sessão funcionando perfeitamente!")
                    return True
                elif status == 'FAILED':
                    print("   ❌ Sessão falhou durante a inicialização")
                    return False
                elif status == 'STARTING':
                    if attempt == 0:
                        print("   📱 QR Code disponível em: http://127.0.0.1:5000/qr_waha")
                        print("   📲 Escaneie o QR code com seu WhatsApp")
                    print("   ⏳ Aguardando escaneamento...")
                else:
                    print(f"   ⚠️ Status inesperado: {status}")
            else:
                print(f"   ❌ Erro ao verificar status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erro na verificação: {e}")
            return False
        
        attempt += 1
        time.sleep(10)  # Aguardar 10 segundos entre verificações
    
    print("   ⏰ Timeout - sessão não conectou dentro do tempo limite")
    return False

def test_session_functionality():
    """Testa a funcionalidade da sessão após conexão"""
    
    base_url = "http://localhost:3000"
    api_key = "waha-key-2025"
    session_name = "default"
    headers = {'X-Api-Key': api_key}
    
    print("\n4️⃣ Testando funcionalidade da sessão...")
    
    try:
        # Verificar se a sessão está funcionando
        response = requests.get(f"{base_url}/api/sessions/{session_name}", headers=headers)
        
        if response.status_code == 200:
            session_data = response.json()
            status = session_data.get('status')
            
            if status == 'WORKING':
                me = session_data.get('me')
                if me:
                    user_id = me.get('id')
                    print(f"   ✅ Sessão ativa - ID: {user_id}")
                    
                    # Testar envio de mensagem para si mesmo
                    print("   📤 Testando envio de mensagem...")
                    
                    test_payload = {
                        "chatId": user_id,
                        "text": "🤖 Teste de conexão WAHA - " + datetime.now().strftime("%H:%M:%S"),
                        "session": session_name
                    }
                    
                    send_response = requests.post(f"{base_url}/api/sendText", 
                                                json=test_payload, headers=headers, timeout=15)
                    
                    if send_response.status_code in [200, 201]:
                        print("   ✅ Mensagem de teste enviada com sucesso!")
                        print("   🎉 Sessão WAHA está funcionando perfeitamente!")
                        return True
                    else:
                        print(f"   ❌ Erro ao enviar mensagem: {send_response.status_code}")
                        return False
                else:
                    print("   ❌ Sessão não tem informações do usuário")
                    return False
            else:
                print(f"   ❌ Sessão não está funcionando - Status: {status}")
                return False
        else:
            print(f"   ❌ Erro ao verificar sessão: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando correção da sessão WAHA...")
    
    # Passo 1: Corrigir a sessão
    if fix_waha_session():
        # Passo 2: Monitorar inicialização
        if monitor_session_startup():
            # Passo 3: Testar funcionalidade
            test_session_functionality()
        else:
            print("\n❌ Falha na inicialização da sessão")
    else:
        print("\n❌ Falha na correção da sessão")
    
    print("\n" + "=" * 40)
    print("🏁 Processo de correção finalizado")