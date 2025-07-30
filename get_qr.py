#!/usr/bin/env python3
import requests
import json
import base64
import time
import webbrowser

def get_qr_code():
    """Obtém o QR code da sessão WAHA"""
    headers = {
        'X-API-KEY': 'waha-key-2025',
        'Content-Type': 'application/json'
    }
    
    try:
        # Verificar status da sessão
        print("🔍 Verificando status da sessão...")
        response = requests.get('http://localhost:3000/api/sessions/default', headers=headers)
        print(f"Status da sessão: {response.status_code}")
        if response.status_code == 200:
            session_data = response.json()
            print(f"Dados da sessão: {json.dumps(session_data, indent=2)}")
            
            # Se o status for SCAN_QR_CODE, tentar diferentes endpoints
            if session_data.get('status') == 'SCAN_QR_CODE':
                print("\n📱 Sessão aguardando QR code. Tentando diferentes endpoints...")
                
                # Lista de possíveis endpoints para QR code
                qr_endpoints = [
                    '/api/sessions/default/qr',
                    '/api/sessions/default/auth/qr',
                    '/api/sessions/default/auth/qr.png',
                    '/api/sessions/default/qr.png',
                    '/api/qr/default',
                    '/api/auth/qr/default'
                ]
                
                for endpoint in qr_endpoints:
                    print(f"\n🔍 Tentando endpoint: {endpoint}")
                    qr_response = requests.get(f'http://localhost:3000{endpoint}', headers=headers)
                    print(f"Status: {qr_response.status_code}")
                    
                    if qr_response.status_code == 200:
                        content_type = qr_response.headers.get('content-type', '')
                        print(f"Content-Type: {content_type}")
                        
                        if 'image' in content_type:
                            # É uma imagem
                            with open('qr_code.png', 'wb') as f:
                                f.write(qr_response.content)
                            print("✅ QR code salvo como 'qr_code.png'")
                            
                            # Abrir a imagem
                            import subprocess
                            subprocess.run(['open', 'qr_code.png'])
                            return True
                            
                        elif 'json' in content_type:
                            # É JSON
                            try:
                                qr_data = qr_response.json()
                                print(f"Dados QR: {json.dumps(qr_data, indent=2)}")
                                
                                # Procurar por campo de QR code
                                qr_fields = ['qr', 'qrCode', 'qr_code', 'image', 'base64']
                                for field in qr_fields:
                                    if field in qr_data and qr_data[field]:
                                        qr_base64 = qr_data[field]
                                        if qr_base64.startswith('data:image'):
                                            qr_base64 = qr_base64.split(',')[1]
                                        
                                        try:
                                            qr_bytes = base64.b64decode(qr_base64)
                                            with open('qr_code.png', 'wb') as f:
                                                f.write(qr_bytes)
                                            print("✅ QR code salvo como 'qr_code.png'")
                                            
                                            import subprocess
                                            subprocess.run(['open', 'qr_code.png'])
                                            return True
                                        except Exception as e:
                                            print(f"⚠️ Erro ao decodificar base64: {e}")
                                            
                            except json.JSONDecodeError:
                                print(f"Resposta não é JSON válido: {qr_response.text[:100]}...")
                        else:
                            print(f"Resposta: {qr_response.text[:200]}...")
                    else:
                        print(f"Erro: {qr_response.text[:100]}...")
                
                print("\n❌ Nenhum QR code encontrado em nenhum endpoint")
                print("\n💡 Dica: Tente acessar http://localhost:3000 no navegador")
                print("    e procure por uma seção de 'Sessions' ou 'QR Code'")
                
                # Abrir a interface web
                webbrowser.open('http://localhost:3000')
                
            else:
                print(f"\n⚠️ Status da sessão não é SCAN_QR_CODE: {session_data.get('status')}")
                if session_data.get('status') == 'WORKING':
                    print("✅ Sessão já está conectada!")
                    return True
        
    except Exception as e:
        print(f"💥 Erro: {e}")
    
    return False

if __name__ == '__main__':
    get_qr_code()