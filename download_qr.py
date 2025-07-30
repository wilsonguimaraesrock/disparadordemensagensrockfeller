#!/usr/bin/env python3
import requests
import base64
from datetime import datetime

def download_qr_code():
    """Baixa o QR code do WAHA e salva como imagem"""
    
    url = 'http://localhost:3000/api/default/auth/qr'
    headers = {'X-Api-Key': 'waha-key-2025'}
    
    try:
        print("Baixando QR code do WAHA...")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # Salva a imagem PNG
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"waha_qr_code_{timestamp}.png"
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ QR code salvo como: {filename}")
            print(f"📱 Abra o arquivo {filename} e escaneie com o WhatsApp")
            print("\n📋 Instruções:")
            print("1. Abra o WhatsApp no seu celular")
            print("2. Vá em Configurações > Aparelhos conectados")
            print("3. Toque em 'Conectar um aparelho'")
            print("4. Escaneie o QR code da imagem salva")
            
            return True
        else:
            print(f"❌ Erro ao baixar QR code: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    download_qr_code()