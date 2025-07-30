#!/usr/bin/env python3
"""
Script para configurar e conectar a instância da Evolution API
"""

import requests
import json
import time

API_KEY = "evolution-api-key-2025"
BASE_URL = "http://localhost:8080"
INSTANCE_NAME = "whatsapp-sender"

def check_api_status():
    """Verifica se a API está rodando"""
    try:
        response = requests.get(f"{BASE_URL}", timeout=5)
        print(f"✅ API Status: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API não está acessível: {e}")
        return False

def create_instance():
    """Cria uma nova instância"""
    url = f"{BASE_URL}/instance/create"
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "instanceName": INSTANCE_NAME,
        "token": API_KEY,
        "qrcode": True,
        "number": "",
        "typebot": {
            "enabled": False
        },
        "webhook": {
            "enabled": False
        },
        "websocket": {
            "enabled": False
        },
        "rabbitmq": {
            "enabled": False
        },
        "sqs": {
            "enabled": False
        },
        "settings": {
            "rejectCall": False,
            "msgCall": "",
            "groupsIgnore": False,
            "alwaysOnline": False,
            "readMessages": False,
            "readStatus": False,
            "syncFullHistory": False
        }
    }
    
    try:
        print(f"🔧 Criando instância '{INSTANCE_NAME}'...")
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ Instância criada com sucesso!")
            return True
        elif response.status_code == 409:
            print("⚠️ Instância já existe")
            return True
        else:
            print(f"❌ Erro ao criar instância: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def get_instance_status():
    """Verifica o status da instância"""
    url = f"{BASE_URL}/instance/connectionState/{INSTANCE_NAME}"
    headers = {
        "apikey": API_KEY
    }
    
    try:
        print(f"🔍 Verificando status da instância '{INSTANCE_NAME}'...")
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            return data
        else:
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def connect_instance():
    """Conecta a instância ao WhatsApp"""
    url = f"{BASE_URL}/instance/connect/{INSTANCE_NAME}"
    headers = {
        "apikey": API_KEY
    }
    
    try:
        print(f"🔗 Conectando instância '{INSTANCE_NAME}'...")
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verificar se há QR Code
            if 'base64' in data:
                print("\n📱 QR Code encontrado!")
                print("💡 Acesse http://localhost:8080/manager para escanear o QR Code")
                print("💡 Ou use o script evolution_api_guide.py para salvar o QR Code")
                return True
            elif 'pairingCode' in data:
                print(f"\n📱 Código de pareamento: {data['pairingCode']}")
                print("💡 Use este código no WhatsApp para conectar")
                return True
            else:
                print("⚠️ QR Code não encontrado na resposta")
                return False
        else:
            print(f"❌ Erro ao conectar: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_send_message(numero_teste):
    """Testa o envio de uma mensagem"""
    url = f"{BASE_URL}/message/sendText/{INSTANCE_NAME}"
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "number": numero_teste.replace('+', '').replace('-', '').replace(' ', ''),
        "text": "🤖 Teste da Evolution API integrada! ✅"
    }
    
    try:
        print(f"📤 Testando envio para {numero_teste}...")
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if 'key' in data or 'messageId' in data:
                print("✅ Mensagem enviada com sucesso!")
                return True
            else:
                print("⚠️ Resposta inesperada")
                return False
        else:
            print(f"❌ Erro no envio: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def main():
    print("🔥 CONFIGURAÇÃO DA EVOLUTION API")
    print("="*50)
    
    # 1. Verificar se a API está rodando
    if not check_api_status():
        print("❌ Evolution API não está rodando")
        print("💡 Execute: docker-compose up -d")
        return
    
    # 2. Criar instância
    if not create_instance():
        print("❌ Falha ao criar instância")
        return
    
    # 3. Verificar status
    status = get_instance_status()
    if not status:
        print("❌ Falha ao verificar status")
        return
    
    instance_state = status.get('instance', {}).get('state')
    print(f"\n📊 Estado da instância: {instance_state}")
    
    # 4. Se não estiver conectada, tentar conectar
    if instance_state != 'open':
        print("\n🔗 Instância não está conectada, tentando conectar...")
        if connect_instance():
            print("\n⏳ Aguarde conectar o WhatsApp e execute novamente para testar")
            print("💡 Acesse: http://localhost:8080/manager")
            print("💡 Login: evolution-api-key-2025")
            return
    else:
        print("✅ Instância já está conectada!")
        
        # 5. Testar envio
        numero_teste = input("\n📱 Digite um número para teste (ex: +5521999998888): ").strip()
        if numero_teste:
            test_send_message(numero_teste)
        
    print("\n" + "="*50)
    print("🎯 CONFIGURAÇÃO CONCLUÍDA")
    print("💡 Agora você pode usar a Evolution API na aplicação!")
    print("💡 Execute: python test_evolution_integration.py")
    print("="*50)

if __name__ == "__main__":
    main()