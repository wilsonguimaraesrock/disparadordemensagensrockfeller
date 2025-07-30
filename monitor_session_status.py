#!/usr/bin/env python3
"""
Script para monitorar o status da sessão WAHA e fornecer instruções
"""

import requests
import json
import time
from datetime import datetime

def monitor_session_status():
    """Monitora o status da sessão WAHA e fornece instruções"""
    
    # Configurações
    base_url = "http://localhost:3000"
    api_key = "waha-key-2025"
    session_name = "default"
    
    headers = {
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    print("🔍 Monitorando Status da Sessão WAHA")
    print("=" * 50)
    
    try:
        # Verificar status da sessão
        response = requests.get(f"{base_url}/api/sessions/{session_name}", headers=headers, timeout=10)
        
        if response.status_code == 200:
            session_data = response.json()
            status = session_data.get('status', 'UNKNOWN')
            
            print(f"📊 Status da Sessão: {status}")
            print(f"🕒 Verificado em: {datetime.now().strftime('%H:%M:%S')}")
            print()
            
            if status == 'STARTING':
                print("🚀 SESSÃO INICIANDO")
                print("⏳ Aguarde alguns segundos para o QR code aparecer...")
                print()
                print("📱 PRÓXIMOS PASSOS:")
                print("1. Abra o dashboard do WAHA: http://localhost:3000/dashboard")
                print("2. Clique na sessão 'default'")
                print("3. Aguarde o QR code aparecer")
                print("4. Escaneie o QR code com seu WhatsApp")
                print("   - Abra o WhatsApp no seu celular")
                print("   - Vá em Configurações > Dispositivos conectados")
                print("   - Toque em 'Conectar um dispositivo'")
                print("   - Escaneie o QR code")
                
            elif status == 'SCAN_QR':
                print("📱 QR CODE DISPONÍVEL")
                print("✅ A sessão está pronta para escaneamento!")
                print()
                print("🔗 Acesse: http://localhost:3000/dashboard")
                print("📱 Escaneie o QR code com seu WhatsApp")
                
            elif status == 'WORKING':
                print("✅ SESSÃO CONECTADA")
                print("🎉 WhatsApp conectado com sucesso!")
                print("📤 Você já pode enviar mensagens")
                
            elif status == 'FAILED':
                print("❌ FALHA NA SESSÃO")
                print("💡 Tente reiniciar a sessão")
                
            else:
                print(f"ℹ️ Status: {status}")
                print("📋 Dados da sessão:")
                print(json.dumps(session_data, indent=2))
                
        else:
            print(f"❌ Erro ao verificar sessão: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print()
    print("🔗 Links úteis:")
    print(f"   Dashboard: http://localhost:3000/dashboard")
    print(f"   Swagger: http://localhost:3000/")
    print(f"   Interface Web: http://127.0.0.1:5000")
    print()
    print("🔄 Execute este script novamente para verificar o status atualizado")

if __name__ == "__main__":
    monitor_session_status()