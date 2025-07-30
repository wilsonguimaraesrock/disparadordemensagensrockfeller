#!/usr/bin/env python3
"""
Script para testar se o QR code está sendo exibido corretamente
"""

import requests
import base64
import json

def test_qr_endpoint():
    """Testa o endpoint do QR code e salva a imagem"""
    try:
        print("🔍 Testando endpoint /api/waha/qr_screenshot...")
        
        # Fazer requisição para o endpoint
        response = requests.post('http://127.0.0.1:5001/api/waha/qr_screenshot')
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                print("✅ Endpoint retornou sucesso!")
                
                # Verificar se há nota
                if 'note' in data:
                    print(f"📝 Nota: {data['note']}")
                
                # Salvar a imagem
                qr_base64 = data.get('qr_code')
                if qr_base64:
                    # Decodificar base64 e salvar
                    image_data = base64.b64decode(qr_base64)
                    
                    with open('qr_captured.png', 'wb') as f:
                        f.write(image_data)
                    
                    print("💾 Imagem salva como 'qr_captured.png'")
                    print(f"📏 Tamanho da imagem: {len(image_data)} bytes")
                    
                    # Tentar abrir a imagem
                    import subprocess
                    try:
                        subprocess.run(['open', 'qr_captured.png'], check=True)
                        print("🖼️ Imagem aberta para visualização")
                    except:
                        print("⚠️ Não foi possível abrir a imagem automaticamente")
                else:
                    print("❌ Nenhum QR code encontrado na resposta")
            else:
                print(f"❌ Endpoint retornou erro: {data.get('error')}")
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao testar endpoint: {e}")

if __name__ == '__main__':
    test_qr_endpoint()