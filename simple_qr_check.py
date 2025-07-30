#!/usr/bin/env python3
import requests
import time
import webbrowser

def check_waha_interface():
    """Verifica a interface web do WAHA para encontrar o QR code"""
    
    print("🔍 Verificando interface web do WAHA...")
    
    try:
        # Tentar acessar a página principal do WAHA
        response = requests.get('http://localhost:3000')
        print(f"Status da página principal: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Interface web do WAHA está acessível")
            print("\n📱 Abrindo interface no navegador...")
            webbrowser.open('http://localhost:3000')
            
            print("\n💡 Instruções:")
            print("1. Na interface web do WAHA, procure por:")
            print("   - Seção 'Sessions'")
            print("   - Botão 'QR Code' ou 'Connect'")
            print("   - Aba 'Authentication'")
            print("2. Se não encontrar, tente:")
            print("   - http://localhost:3000/sessions")
            print("   - http://localhost:3000/dashboard")
            print("   - http://localhost:3000/auth")
            
            # Tentar algumas URLs específicas
            test_urls = [
                'http://localhost:3000/sessions',
                'http://localhost:3000/dashboard', 
                'http://localhost:3000/auth',
                'http://localhost:3000/qr',
                'http://localhost:3000/connect'
            ]
            
            print("\n🔍 Testando URLs específicas...")
            for url in test_urls:
                try:
                    test_response = requests.get(url)
                    if test_response.status_code == 200:
                        print(f"✅ {url} - Acessível")
                        webbrowser.open(url)
                        break
                    else:
                        print(f"❌ {url} - Status {test_response.status_code}")
                except:
                    print(f"❌ {url} - Erro de conexão")
        else:
            print(f"❌ Erro ao acessar interface: {response.status_code}")
            
    except Exception as e:
        print(f"💥 Erro: {e}")
        
    # Verificar status da sessão
    print("\n🔍 Verificando status da sessão WAHA...")
    try:
        headers = {'X-API-KEY': 'waha-key-2025'}
        session_response = requests.get('http://localhost:3000/api/sessions/default', headers=headers)
        
        if session_response.status_code == 200:
            session_data = session_response.json()
            status = session_data.get('status', 'UNKNOWN')
            print(f"📊 Status da sessão: {status}")
            
            if status == 'SCAN_QR_CODE':
                print("\n📱 A sessão está aguardando o QR code!")
                print("💡 O QR code deve estar visível na interface web do WAHA")
                print("🌐 Acesse: http://localhost:3000")
            elif status == 'WORKING':
                print("✅ WhatsApp já está conectado!")
            else:
                print(f"⚠️ Status inesperado: {status}")
        else:
            print(f"❌ Erro ao verificar sessão: {session_response.status_code}")
            
    except Exception as e:
        print(f"💥 Erro ao verificar sessão: {e}")

if __name__ == '__main__':
    check_waha_interface()