#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

API_URL = "http://localhost:8080"
API_KEY = "evolution-api-key-2025"
INSTANCE_NAME = "whatsapp-sender"

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

def test_endpoint(method, endpoint, data=None):
    """Testa um endpoint da API e retorna a resposta"""
    try:
        url = f"{API_URL}{endpoint}"
        print(f"\n🔍 Testando {method} {url}")
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        print(f"📊 Status Code: {response.status_code}")
        
        try:
            response_json = response.json()
            print(f"📋 Resposta: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
            return response_json
        except:
            print(f"📋 Resposta (texto): {response.text}")
            return response.text
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def main():
    print("🔧 Diagnóstico Evolution API - QR Code")
    print("=" * 50)
    
    # 1. Verificar se a API está funcionando
    print("\n1️⃣ Verificando status da API...")
    test_endpoint("GET", "/")
    
    # 2. Listar todas as instâncias
    print("\n2️⃣ Listando instâncias...")
    instances = test_endpoint("GET", "/instance/fetchInstances")
    
    # 3. Verificar status da instância específica
    print(f"\n3️⃣ Verificando status da instância {INSTANCE_NAME}...")
    test_endpoint("GET", f"/instance/connectionState/{INSTANCE_NAME}")
    
    # 4. Tentar deletar a instância existente
    print(f"\n4️⃣ Deletando instância {INSTANCE_NAME}...")
    test_endpoint("DELETE", f"/instance/delete/{INSTANCE_NAME}")
    
    # Aguardar um pouco
    print("\n⏳ Aguardando 3 segundos...")
    time.sleep(3)
    
    # 5. Criar nova instância com configurações específicas para QR
    print(f"\n5️⃣ Criando nova instância {INSTANCE_NAME}...")
    instance_config = {
        "instanceName": INSTANCE_NAME,
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS",
        "webhookUrl": "",
        "webhookByEvents": False,
        "webhookBase64": False,
        "markMessagesRead": True,
        "delayMessage": 1000,
        "alwaysOnline": False,
        "readMessages": False,
        "readStatus": False,
        "syncFullHistory": False
    }
    
    create_result = test_endpoint("POST", "/instance/create", instance_config)
    
    # Aguardar um pouco
    print("\n⏳ Aguardando 5 segundos para inicialização...")
    time.sleep(5)
    
    # 6. Tentar conectar a instância
    print(f"\n6️⃣ Conectando instância {INSTANCE_NAME}...")
    test_endpoint("GET", f"/instance/connect/{INSTANCE_NAME}")
    
    # Aguardar um pouco
    print("\n⏳ Aguardando 3 segundos...")
    time.sleep(3)
    
    # 7. Verificar status após conexão
    print(f"\n7️⃣ Verificando status após conexão...")
    test_endpoint("GET", f"/instance/connectionState/{INSTANCE_NAME}")
    
    # 8. Tentar diferentes endpoints para QR code
    print("\n8️⃣ Testando diferentes endpoints para QR code...")
    
    qr_endpoints = [
        f"/instance/qrcode/{INSTANCE_NAME}",
        f"/instance/{INSTANCE_NAME}/qrcode",
        f"/instance/qr/{INSTANCE_NAME}",
        f"/qrcode/{INSTANCE_NAME}",
        f"/instance/fetchQrCode/{INSTANCE_NAME}"
    ]
    
    for endpoint in qr_endpoints:
        test_endpoint("GET", endpoint)
    
    # 9. Verificar se há webhooks ou eventos
    print("\n9️⃣ Verificando eventos/webhooks...")
    test_endpoint("GET", f"/webhook/find/{INSTANCE_NAME}")
    
    print("\n✅ Diagnóstico concluído!")
    print("\n💡 Dicas:")
    print("- Se o QR code não aparecer, pode ser que a instância já esteja conectada")
    print("- Verifique se há alguma sessão salva que precisa ser limpa")
    print("- Tente acessar a interface web em http://localhost:8080/manager")

if __name__ == "__main__":
    main()