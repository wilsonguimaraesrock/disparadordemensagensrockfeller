#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para Evolution API - Envio de Mídia
"""

import requests
import json
import time

# Configurações
EVOLUTION_URL = "http://localhost:8080"
API_KEY = "evolution-api-key-2025"
INSTANCE_NAME = "whatsapp-sender"
TEST_PHONE = "5547996083460"  # Substitua pelo seu número

def check_connection():
    """Verifica se a instância está conectada"""
    try:
        response = requests.get(
            f"{EVOLUTION_URL}/instance/connectionState/{INSTANCE_NAME}",
            headers={'apikey': API_KEY}
        )
        
        if response.status_code == 200:
            result = response.json()
            status = result.get('instance', {}).get('state', 'unknown')
            print(f"📱 Status: {status}")
            return status == 'open'
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def create_instance():
    """Cria uma instância WhatsApp na Evolution API"""
    print(f"📱 Criando instância '{INSTANCE_NAME}'...")
    
    data = {
        "instanceName": INSTANCE_NAME,
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS"
    }
    
    try:
        response = requests.post(
            f"{EVOLUTION_URL}/instance/create",
            json=data,
            headers={
                'Content-Type': 'application/json',
                'apikey': API_KEY
            }
        )
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Instância criada com sucesso!")
            print(f"📋 Detalhes: {json.dumps(result, indent=2)}")
            return True
        elif response.status_code == 409 or response.status_code == 403:
            print("ℹ️ Instância já existe")
            return True
        else:
            print(f"❌ Erro ao criar instância: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def get_qr_code():
    """Obtém o QR Code para conectar o WhatsApp"""
    print("📱 Obtendo QR Code...")
    
    try:
        response = requests.get(
            f"{EVOLUTION_URL}/instance/connect/{INSTANCE_NAME}",
            headers={'apikey': API_KEY}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"📋 Resposta completa: {json.dumps(result, indent=2)}")
            
            # Verifica diferentes formatos possíveis de QR Code
            qr_data = None
            if 'base64' in result:
                qr_data = result['base64']
            elif 'qrcode' in result and 'base64' in result['qrcode']:
                qr_data = result['qrcode']['base64']
            elif 'pairingCode' in result:
                print(f"📱 Código de pareamento: {result['pairingCode']}")
                print("📱 Use este código no seu WhatsApp em Dispositivos Conectados > Conectar um dispositivo")
                return True
            
            if qr_data:
                # Salva o QR Code como imagem
                import base64
                if qr_data.startswith('data:image'):
                    qr_data = qr_data.split(',')[1]  # Remove o prefixo data:image/png;base64,
                
                with open('evolution_qr_code.png', 'wb') as f:
                    f.write(base64.b64decode(qr_data))
                
                print("✅ QR Code salvo como 'evolution_qr_code.png'")
                print("📱 Escaneie o QR Code com seu WhatsApp para conectar!")
                return True
            else:
                print("❌ QR Code não encontrado na resposta")
                return False
        else:
            print(f"❌ Erro ao obter QR Code: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def send_text_message():
    """Testa envio de mensagem de texto"""
    print("\n📝 Testando envio de texto...")
    
    data = {
        "number": TEST_PHONE,
        "text": "🤖 Teste Evolution API\n\nSe você recebeu esta mensagem, a Evolution API está funcionando!"
    }
    
    try:
        response = requests.post(
            f"{EVOLUTION_URL}/message/sendText/{INSTANCE_NAME}",
            json=data,
            headers={
                'Content-Type': 'application/json',
                'apikey': API_KEY
            }
        )
        
        if response.status_code == 201:
            print("✅ Texto enviado com sucesso!")
            return True
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def send_image():
    """Testa envio de imagem"""
    print("\n🖼️ Testando envio de imagem...")
    
    data = {
        "number": TEST_PHONE,
        "mediaMessage": {
            "mediatype": "image",
            "media": "https://github.com/devlikeapro/waha/raw/core/examples/dev.likeapro.jpg",
            "caption": "🖼️ Teste de imagem via Evolution API\n\nSe você recebeu esta imagem, o envio de mídia está funcionando!"
        }
    }
    
    try:
        response = requests.post(
            f"{EVOLUTION_URL}/message/sendMedia/{INSTANCE_NAME}",
            json=data,
            headers={
                'Content-Type': 'application/json',
                'apikey': API_KEY
            }
        )
        
        if response.status_code == 201:
            print("✅ Imagem enviada com sucesso!")
            return True
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def send_video():
    """Testa envio de vídeo"""
    print("\n🎥 Testando envio de vídeo...")
    
    data = {
        "number": TEST_PHONE,
        "mediaMessage": {
            "mediatype": "video",
            "media": "https://github.com/devlikeapro/waha/raw/core/examples/video.mp4",
            "caption": "🎥 Teste de vídeo via Evolution API\n\nSe você recebeu este vídeo, o envio de mídia está funcionando perfeitamente!"
        }
    }
    
    try:
        response = requests.post(
            f"{EVOLUTION_URL}/message/sendMedia/{INSTANCE_NAME}",
            json=data,
            headers={
                'Content-Type': 'application/json',
                'apikey': API_KEY
            }
        )
        
        if response.status_code == 201:
            print("✅ Vídeo enviado com sucesso!")
            return True
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    print("🚀 Testando Evolution API")
    print("="*40)
    
    # Primeiro, tenta criar a instância
    if not create_instance():
        print("❌ Falha ao criar instância")
        return
    
    # Verifica se já está conectada
    if check_connection():
        print("✅ Instância já conectada! Iniciando testes...")
        
        # Testes
        send_text_message()
        time.sleep(2)
        
        send_image()
        time.sleep(2)
        
        send_video()
        
        print("\n🎉 Testes concluídos!")
    else:
        print("📱 Instância não está conectada. Obtendo QR Code...")
        if get_qr_code():
            print("\n📱 PRÓXIMOS PASSOS:")
            print("1. Abra o arquivo 'evolution_qr_code.png'")
            print("2. Escaneie o QR Code com seu WhatsApp")
            print("3. Execute este script novamente para testar")
        else:
            print("❌ Falha ao obter QR Code")

if __name__ == "__main__":
    main()