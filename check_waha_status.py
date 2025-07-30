#!/usr/bin/env python3
"""
Script para verificar o status da sessão WAHA
"""

import requests
import json
import time

def check_waha_session_status():
    """Verifica o status da sessão WAHA"""
    
    # Configurações WAHA
    base_url = "http://localhost:3000"
    api_key = "waha-key-2025"
    session_name = "default"
    
    print("🔍 Verificando status da sessão WAHA")
    print("=" * 50)
    
    try:
        session_url = f"{base_url}/api/sessions/{session_name}"
        headers = {
            'X-Api-Key': api_key,
            'Content-Type': 'application/json'
        }
        
        response = requests.get(session_url, headers=headers)
        print(f"📊 Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            session_data = response.json()
            print(f"📋 Dados da sessão:")
            print(json.dumps(session_data, indent=2))
            
            status = session_data.get('status', 'unknown')
            print(f"\n🎯 Status atual: {status}")
            
            if status == 'WORKING':
                print("✅ Sessão está funcionando! Pronta para enviar mensagens.")
                return True
            elif status == 'STARTING':
                print("⏳ Sessão está iniciando. QR code pode estar disponível.")
                print("📱 Escaneie o QR code em: http://127.0.0.1:5000/qr_waha")
                return False
            elif status == 'STOPPED':
                print("❌ Sessão está parada. Precisa ser reiniciada.")
                return False
            elif status == 'FAILED':
                print("💥 Sessão falhou. Verifique os logs do WAHA.")
                return False
            else:
                print(f"❓ Status desconhecido: {status}")
                return False
        else:
            print(f"❌ Erro ao verificar sessão: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Exceção ao verificar sessão: {e}")
        return False

def wait_for_working_status(max_wait_minutes=5):
    """Aguarda a sessão ficar em status WORKING"""
    
    print(f"\n⏰ Aguardando sessão ficar WORKING (máximo {max_wait_minutes} minutos)...")
    
    max_attempts = max_wait_minutes * 6  # 6 tentativas por minuto (10s cada)
    
    for attempt in range(max_attempts):
        print(f"\n🔄 Tentativa {attempt + 1}/{max_attempts}")
        
        if check_waha_session_status():
            print("\n🎉 Sessão está pronta para uso!")
            return True
        
        if attempt < max_attempts - 1:
            print("⏳ Aguardando 10 segundos...")
            time.sleep(10)
    
    print(f"\n⏰ Timeout: Sessão não ficou pronta em {max_wait_minutes} minutos")
    return False

def get_qr_code_info():
    """Tenta obter informações sobre o QR code"""
    
    print("\n📱 Verificando QR code...")
    
    try:
        # Tentar via API local
        qr_url = "http://127.0.0.1:5000/api/waha/qr/default"
        response = requests.get(qr_url)
        
        print(f"📊 Status QR (API local): {response.status_code}")
        
        if response.status_code == 200:
            print("✅ QR code disponível via API local")
        else:
            print(f"❌ QR code não disponível: {response.text}")
            
    except Exception as e:
        print(f"💥 Erro ao verificar QR code: {e}")

if __name__ == "__main__":
    print("🚀 Verificador de Status WAHA")
    print("=" * 50)
    
    # Verificação inicial
    if check_waha_session_status():
        print("\n🎉 Sessão já está funcionando!")
    else:
        print("\n⚠️ Sessão não está funcionando.")
        
        # Verificar QR code
        get_qr_code_info()
        
        # Perguntar se deve aguardar
        print("\n❓ Deseja aguardar a sessão ficar pronta? (y/n): ", end="")
        choice = input().lower().strip()
        
        if choice in ['y', 'yes', 's', 'sim']:
            wait_for_working_status()
        else:
            print("\n📋 Para ativar a sessão:")
            print("1. Acesse: http://127.0.0.1:5000/qr_waha")
            print("2. Escaneie o QR code com seu WhatsApp")
            print("3. Execute este script novamente para verificar")
    
    print("\n🏁 Verificação concluída")