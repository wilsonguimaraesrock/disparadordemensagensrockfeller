#!/usr/bin/env python3
"""
Script completo para configurar uma sessão WAHA funcional
"""

import requests
import json
import time
from datetime import datetime

def setup_waha_session():
    """Configura uma sessão WAHA completa e funcional"""
    
    # Configurações
    base_url = "http://localhost:3000"
    api_key = "waha-key-2025"
    session_name = "default"
    
    headers = {
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    print("🚀 Configurando Sessão WAHA Completa")
    print("=" * 50)
    
    try:
        # 1. Verificar se o servidor está funcionando
        print("1️⃣ Verificando servidor WAHA...")
        response = requests.get(f"{base_url}/api/sessions", headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"❌ Servidor não está respondendo: {response.status_code}")
            return False
        print("✅ Servidor WAHA está funcionando")
        
        # 2. Listar sessões existentes
        print("\n2️⃣ Verificando sessões existentes...")
        sessions = response.json()
        print(f"📋 Sessões encontradas: {len(sessions)}")
        
        # 3. Remover sessão existente se houver
        session_exists = False
        for session in sessions:
            if session.get('name') == session_name:
                session_exists = True
                print(f"🗑️ Removendo sessão existente: {session_name}")
                delete_response = requests.delete(
                    f"{base_url}/api/sessions/{session_name}", 
                    headers=headers
                )
                print(f"   Status da remoção: {delete_response.status_code}")
                time.sleep(2)
                break
        
        if not session_exists:
            print(f"ℹ️ Sessão '{session_name}' não existe ainda")
        
        # 4. Criar nova sessão
        print(f"\n3️⃣ Criando nova sessão '{session_name}'...")
        
        # Tentar diferentes payloads
        payloads = [
            {'name': session_name},
            {'name': session_name, 'config': {}},
            {'name': session_name, 'config': {'webhooks': []}},
            {
                'name': session_name,
                'config': {
                    'webhooks': [],
                    'debug': False,
                    'nowait': {
                        'store': True,
                        'full': True
                    }
                }
            }
        ]
        
        session_created = False
        for i, payload in enumerate(payloads, 1):
            print(f"   Tentativa {i}: {json.dumps(payload)}")
            create_response = requests.post(
                f"{base_url}/api/sessions", 
                headers=headers, 
                json=payload
            )
            print(f"   Status: {create_response.status_code}")
            
            if create_response.status_code == 201:
                print(f"   Resposta: {create_response.text}")
                
                # Verificar se a sessão foi realmente criada
                time.sleep(2)
                check_response = requests.get(f"{base_url}/api/sessions", headers=headers)
                if check_response.status_code == 200:
                    sessions_after = check_response.json()
                    session_found = any(s.get('name') == session_name for s in sessions_after)
                    
                    if session_found:
                        print("✅ Sessão criada e confirmada!")
                        session_created = True
                        break
                    else:
                        print("⚠️ Sessão criada mas não encontrada na lista")
                else:
                    print(f"❌ Erro ao verificar sessões: {check_response.status_code}")
            else:
                print(f"   Erro: {create_response.text}")
        
        if not session_created:
            print("❌ Falha ao criar sessão")
            return False
        
        # 5. Iniciar a sessão
        print(f"\n4️⃣ Iniciando sessão '{session_name}'...")
        start_response = requests.post(
            f"{base_url}/api/sessions/{session_name}/start", 
            headers=headers
        )
        print(f"Status do início: {start_response.status_code}")
        print(f"Resposta: {start_response.text}")
        
        if start_response.status_code not in [200, 201]:
            print("⚠️ Possível problema ao iniciar sessão")
        
        # 6. Monitorar status da sessão
        print(f"\n5️⃣ Monitorando status da sessão...")
        for attempt in range(10):
            time.sleep(3)
            status_response = requests.get(
                f"{base_url}/api/sessions/{session_name}", 
                headers=headers
            )
            
            if status_response.status_code == 200:
                session_data = status_response.json()
                status = session_data.get('status', 'UNKNOWN')
                print(f"   Tentativa {attempt + 1}: Status = {status}")
                
                if status == 'SCAN_QR':
                    print("\n🎉 SUCESSO! Sessão pronta para escaneamento!")
                    print("=" * 50)
                    print("📱 PRÓXIMOS PASSOS:")
                    print(f"1. Abra: http://localhost:3000/dashboard")
                    print(f"2. Clique na sessão '{session_name}'")
                    print("3. Escaneie o QR code com seu WhatsApp")
                    print("\n📋 Dados da sessão:")
                    print(json.dumps(session_data, indent=2))
                    return True
                    
                elif status == 'WORKING':
                    print("\n✅ SESSÃO JÁ CONECTADA!")
                    print("🎉 WhatsApp já está conectado e funcionando!")
                    return True
                    
                elif status == 'FAILED':
                    print("\n❌ Sessão falhou")
                    print(f"📋 Dados: {json.dumps(session_data, indent=2)}")
                    return False
                    
            else:
                print(f"   Tentativa {attempt + 1}: Erro {status_response.status_code}")
                if status_response.status_code == 404:
                    print("   Sessão não encontrada")
                    break
        
        print("\n⚠️ Timeout ao aguardar status da sessão")
        return False
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    finally:
        print("\n🔗 Links úteis:")
        print(f"   Dashboard: {base_url}/dashboard")
        print(f"   API Docs: {base_url}/")
        print(f"   Interface Web: http://127.0.0.1:5000")

if __name__ == "__main__":
    success = setup_waha_session()
    if success:
        print("\n🎯 Configuração concluída com sucesso!")
    else:
        print("\n💡 Tente executar o script novamente ou verifique os logs do Docker")
        print("   docker logs waha-production --tail 50")