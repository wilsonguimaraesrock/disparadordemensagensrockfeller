#!/usr/bin/env python3
"""
Script para reiniciar completamente a sessão WAHA
"""

import requests
import json
import time

def restart_waha_session():
    """Reinicia completamente a sessão WAHA"""
    
    # Configurações WAHA
    base_url = "http://localhost:3000"
    api_key = "waha-key-2025"
    session_name = "default"
    
    print("🔄 Reiniciando sessão WAHA completamente")
    print("=" * 50)
    
    # Passo 1: Parar a sessão
    print("\n1️⃣ Parando sessão atual...")
    stop_session(base_url, api_key, session_name)
    
    # Aguardar um pouco
    print("⏳ Aguardando 3 segundos...")
    time.sleep(3)
    
    # Passo 2: Iniciar nova sessão
    print("\n2️⃣ Iniciando nova sessão...")
    start_session(base_url, api_key, session_name)
    
    # Passo 3: Verificar status
    print("\n3️⃣ Verificando status...")
    check_status(base_url, api_key, session_name)
    
    print("\n" + "=" * 50)
    print("🏁 Reinicialização concluída")
    print("📱 Acesse http://127.0.0.1:5000/qr_waha para escanear o QR code")

def stop_session(base_url, api_key, session_name):
    """Para a sessão WAHA"""
    try:
        url = f"{base_url}/api/sessions/{session_name}/stop"
        headers = {'X-Api-Key': api_key}
        
        response = requests.post(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            print("   ✅ Sessão parada com sucesso")
        elif response.status_code == 422:
            data = response.json()
            if "already stopped" in data.get('error', '').lower():
                print("   ℹ️ Sessão já estava parada")
            else:
                print(f"   ⚠️ Aviso: {data.get('error', 'Erro desconhecido')}")
        else:
            print(f"   ❌ Erro ao parar sessão: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Detalhes: {error_data}")
            except:
                print(f"   Resposta: {response.text}")
                
    except Exception as e:
        print(f"   ❌ Exceção ao parar sessão: {e}")

def start_session(base_url, api_key, session_name):
    """Inicia a sessão WAHA"""
    try:
        url = f"{base_url}/api/sessions/{session_name}/start"
        headers = {'X-Api-Key': api_key}
        
        response = requests.post(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            print("   ✅ Sessão iniciada com sucesso")
        elif response.status_code == 422:
            data = response.json()
            if "already started" in data.get('error', '').lower():
                print("   ℹ️ Sessão já estava iniciada")
            else:
                print(f"   ⚠️ Aviso: {data.get('error', 'Erro desconhecido')}")
        else:
            print(f"   ❌ Erro ao iniciar sessão: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Detalhes: {error_data}")
            except:
                print(f"   Resposta: {response.text}")
                
    except Exception as e:
        print(f"   ❌ Exceção ao iniciar sessão: {e}")

def check_status(base_url, api_key, session_name):
    """Verifica o status da sessão"""
    try:
        url = f"{base_url}/api/sessions/{session_name}"
        headers = {'X-Api-Key': api_key}
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'UNKNOWN')
            
            print(f"   📊 Status atual: {status}")
            
            if status == 'WORKING':
                print("   ✅ Sessão está funcionando!")
                me = data.get('me')
                if me:
                    print(f"   👤 Usuário: {me.get('pushname', 'N/A')} ({me.get('id', 'N/A')})")
            elif status == 'STARTING':
                print("   ⏳ Sessão está iniciando - QR code disponível")
            elif status == 'STOPPED':
                print("   ⛔ Sessão está parada")
            elif status == 'FAILED':
                print("   ❌ Sessão falhou")
            else:
                print(f"   ❓ Status desconhecido: {status}")
                
        else:
            print(f"   ❌ Erro ao verificar status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Exceção ao verificar status: {e}")

if __name__ == "__main__":
    restart_waha_session()