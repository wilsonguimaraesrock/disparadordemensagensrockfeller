#!/usr/bin/env python3
"""
Script para iniciar sessão WAHA
"""

import requests
import json

def start_waha_session():
    """Inicia uma nova sessão WAHA através da API local"""
    
    print("🚀 Iniciando sessão WAHA...")
    
    # URL da API local
    url = "http://127.0.0.1:5000/api/waha/session/start"
    
    # Dados para iniciar a sessão
    data = {
        "session": "default"
    }
    
    try:
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code in [200, 201]:
            result = response.json()
            if result.get('success'):
                print("✅ Sessão WAHA iniciada com sucesso!")
                print(f"📊 Dados da sessão: {result.get('data', {})}")
                
                # Aguardar um pouco e verificar o QR code
                print("\n🔍 Aguardando QR code ficar disponível...")
                import time
                time.sleep(3)
                
                # Tentar obter o QR code
                qr_url = "http://127.0.0.1:5000/api/waha/qr/default"
                qr_response = requests.get(qr_url)
                
                if qr_response.status_code == 200:
                    qr_data = qr_response.json()
                    if qr_data.get('success'):
                        print("✅ QR code disponível!")
                        print("📱 Acesse a interface web para escanear o QR code:")
                        print("🌐 http://127.0.0.1:5000/qr_waha")
                    else:
                        print("⚠️ QR code ainda não disponível. Tente novamente em alguns segundos.")
                else:
                    print("⚠️ Erro ao obter QR code. Verifique a interface web.")
                
                return True
            else:
                print(f"❌ Erro: {result.get('error', 'Erro desconhecido')}")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor.")
        print("💡 Certifique-se de que o servidor está rodando em http://127.0.0.1:5000")
        return False
    except requests.exceptions.Timeout:
        print("❌ Erro: Timeout na requisição.")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
        return False

if __name__ == "__main__":
    success = start_waha_session()
    if success:
        print("\n🎉 Sessão WAHA iniciada com sucesso!")
        print("📱 Acesse http://127.0.0.1:5000/qr_waha para escanear o QR code")
    else:
        print("\n❌ Falha ao iniciar sessão WAHA")