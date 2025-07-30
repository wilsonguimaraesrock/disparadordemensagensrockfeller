#!/usr/bin/env python3
"""
Script para diagnosticar problemas com o servidor WAHA
"""

import requests
import json
import time
from datetime import datetime

def diagnose_waha_issue():
    """Diagnostica problemas com o servidor WAHA"""
    
    # Configurações WAHA
    base_url = "http://localhost:3000"
    api_key = "waha-key-2025"
    session_name = "default"
    
    print("🔍 Diagnóstico do Servidor WAHA")
    print("=" * 50)
    
    # Teste 1: Verificar se o servidor está respondendo
    print("\n1️⃣ Testando conectividade do servidor...")
    test_server_connectivity(base_url)
    
    # Teste 2: Verificar autenticação
    print("\n2️⃣ Testando autenticação...")
    test_authentication(base_url, api_key)
    
    # Teste 3: Listar todas as sessões
    print("\n3️⃣ Listando sessões existentes...")
    list_sessions(base_url, api_key)
    
    # Teste 4: Verificar status da sessão default
    print("\n4️⃣ Verificando sessão default...")
    check_session_details(base_url, api_key, session_name)
    
    # Teste 5: Tentar deletar e recriar a sessão
    print("\n5️⃣ Tentando deletar e recriar sessão...")
    recreate_session(base_url, api_key, session_name)
    
    # Teste 6: Verificar logs do WAHA (se disponível)
    print("\n6️⃣ Verificando informações do sistema...")
    check_system_info(base_url, api_key)
    
    print("\n" + "=" * 50)
    print("🏁 Diagnóstico concluído")

def test_server_connectivity(base_url):
    """Testa se o servidor WAHA está respondendo"""
    try:
        response = requests.get(f"{base_url}/api/version", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Servidor respondendo - Versão: {data.get('version', 'N/A')}")
            return True
        else:
            print(f"   ❌ Servidor retornou status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Não foi possível conectar ao servidor WAHA")
        print("   💡 Verifique se o servidor WAHA está rodando na porta 3000")
        return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def test_authentication(base_url, api_key):
    """Testa a autenticação com a API"""
    try:
        headers = {'X-Api-Key': api_key}
        response = requests.get(f"{base_url}/api/sessions", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("   ✅ Autenticação válida")
            return True
        elif response.status_code == 401:
            print("   ❌ Falha na autenticação - API Key inválida")
            return False
        else:
            print(f"   ⚠️ Status inesperado: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def list_sessions(base_url, api_key):
    """Lista todas as sessões existentes"""
    try:
        headers = {'X-Api-Key': api_key}
        response = requests.get(f"{base_url}/api/sessions", headers=headers, timeout=10)
        
        if response.status_code == 200:
            sessions = response.json()
            print(f"   📋 Total de sessões: {len(sessions)}")
            
            for session in sessions:
                name = session.get('name', 'N/A')
                status = session.get('status', 'N/A')
                engine = session.get('engine', {}).get('engine', 'N/A')
                print(f"   - {name}: {status} ({engine})")
            
            return sessions
        else:
            print(f"   ❌ Erro ao listar sessões: {response.status_code}")
            return []
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return []

def check_session_details(base_url, api_key, session_name):
    """Verifica detalhes da sessão específica"""
    try:
        headers = {'X-Api-Key': api_key}
        response = requests.get(f"{base_url}/api/sessions/{session_name}", headers=headers, timeout=10)
        
        if response.status_code == 200:
            session = response.json()
            status = session.get('status', 'N/A')
            engine = session.get('engine', {})
            config = session.get('config', {})
            
            print(f"   📊 Status: {status}")
            print(f"   🔧 Engine: {engine.get('engine', 'N/A')}")
            print(f"   🌐 WebJS Version: {engine.get('WWebVersion', 'N/A')}")
            print(f"   ⚙️ Webhooks: {len(config.get('webhooks', []))}")
            
            if session.get('me'):
                me = session['me']
                print(f"   👤 Conectado como: {me.get('pushname', 'N/A')} ({me.get('id', 'N/A')})")
            else:
                print("   👤 Não conectado")
                
            return session
        elif response.status_code == 404:
            print("   ❌ Sessão não encontrada")
            return None
        else:
            print(f"   ❌ Erro: {response.status_code}")
            return None
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return None

def recreate_session(base_url, api_key, session_name):
    """Tenta deletar e recriar a sessão"""
    headers = {'X-Api-Key': api_key}
    
    # Tentar deletar a sessão existente
    try:
        print("   🗑️ Deletando sessão existente...")
        response = requests.delete(f"{base_url}/api/sessions/{session_name}", headers=headers, timeout=10)
        
        if response.status_code in [200, 404]:
            print("   ✅ Sessão deletada (ou não existia)")
        else:
            print(f"   ⚠️ Status ao deletar: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro ao deletar: {e}")
    
    # Aguardar um pouco
    time.sleep(2)
    
    # Tentar criar nova sessão
    try:
        print("   🆕 Criando nova sessão...")
        payload = {
            "name": session_name,
            "config": {
                "proxy": None,
                "webhooks": []
            }
        }
        
        response = requests.post(f"{base_url}/api/sessions", 
                               json=payload, headers=headers, timeout=10)
        
        if response.status_code in [200, 201]:
            print("   ✅ Nova sessão criada")
            
            # Aguardar e iniciar
            time.sleep(2)
            print("   🚀 Iniciando sessão...")
            
            start_response = requests.post(f"{base_url}/api/sessions/{session_name}/start", 
                                         headers=headers, timeout=10)
            
            if start_response.status_code in [200, 201]:
                print("   ✅ Sessão iniciada com sucesso")
                return True
            else:
                print(f"   ❌ Erro ao iniciar: {start_response.status_code}")
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
        print(f"   ❌ Erro ao criar sessão: {e}")
        return False

def check_system_info(base_url, api_key):
    """Verifica informações do sistema WAHA"""
    try:
        headers = {'X-Api-Key': api_key}
        
        # Tentar obter informações do sistema
        endpoints = [
            ('/api/version', 'Versão'),
            ('/api/server/status', 'Status do Servidor'),
            ('/api/health', 'Health Check')
        ]
        
        for endpoint, description in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ {description}: {json.dumps(data, indent=2)[:100]}...")
                else:
                    print(f"   ⚠️ {description}: Status {response.status_code}")
            except:
                print(f"   ❌ {description}: Não disponível")
                
    except Exception as e:
        print(f"   ❌ Erro: {e}")

if __name__ == "__main__":
    diagnose_waha_issue()