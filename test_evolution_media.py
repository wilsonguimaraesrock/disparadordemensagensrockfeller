#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Simplificado - Evolution API - Envio de Mídia
Este script testa diretamente o envio de mídia, assumindo que a instância já está conectada.
"""

import requests
import json

# Configurações
EVOLUTION_URL = "http://localhost:8080"
API_KEY = "evolution-api-key-2025"
INSTANCE_NAME = "whatsapp-sender"
TEST_PHONE = "5547996083460"  # Substitua pelo seu número

def check_instance_status():
    """Verifica o status da instância"""
    try:
        response = requests.get(
            f"{EVOLUTION_URL}/instance/connectionState/{INSTANCE_NAME}",
            headers={'apikey': API_KEY}
        )
        
        if response.status_code == 200:
            result = response.json()
            status = result.get('instance', {}).get('state', 'unknown')
            print(f"📱 Status da instância: {status}")
            return status
        else:
            print(f"❌ Erro ao verificar status: {response.status_code}")
            return 'error'
    except Exception as e:
        print(f"❌ Erro: {e}")
        return 'error'

def send_text_message():
    """Testa envio de mensagem de texto"""
    print("\n📝 Testando envio de texto...")
    
    data = {
        "number": TEST_PHONE,
        "text": "🤖 Teste Evolution API\n\n✅ Se você recebeu esta mensagem, a Evolution API está funcionando!\n\n🎯 Próximo teste: envio de mídia"
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
            result = response.json()
            print("✅ Texto enviado com sucesso!")
            print(f"📋 ID da mensagem: {result.get('key', {}).get('id', 'N/A')}")
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
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
            "caption": "🖼️ Teste de imagem via Evolution API\n\n✅ Se você recebeu esta imagem, o envio de mídia está funcionando!\n\n🎉 Parabéns! A Evolution API pode substituir o WAHA Core para envio de mídia."
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
            result = response.json()
            print("✅ Imagem enviada com sucesso!")
            print(f"📋 ID da mensagem: {result.get('key', {}).get('id', 'N/A')}")
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
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
            "caption": "🎥 Teste de vídeo via Evolution API\n\n✅ Se você recebeu este vídeo, o envio de mídia está funcionando perfeitamente!\n\n🚀 A Evolution API é uma excelente alternativa ao WAHA Core!"
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
            result = response.json()
            print("✅ Vídeo enviado com sucesso!")
            print(f"📋 ID da mensagem: {result.get('key', {}).get('id', 'N/A')}")
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def send_document():
    """Testa envio de documento"""
    print("\n📄 Testando envio de documento...")
    
    data = {
        "number": TEST_PHONE,
        "mediaMessage": {
            "mediatype": "document",
            "media": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            "fileName": "teste_evolution_api.pdf",
            "caption": "📄 Teste de documento via Evolution API\n\n✅ Se você recebeu este PDF, todos os tipos de mídia estão funcionando!"
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
            result = response.json()
            print("✅ Documento enviado com sucesso!")
            print(f"📋 ID da mensagem: {result.get('key', {}).get('id', 'N/A')}")
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    print("🚀 Teste de Mídia - Evolution API")
    print("="*50)
    
    # Verifica status da instância
    status = check_instance_status()
    
    if status == 'open':
        print("✅ Instância conectada! Iniciando testes de mídia...")
        
        # Executa todos os testes
        tests = [
            ("Texto", send_text_message),
            ("Imagem", send_image),
            ("Vídeo", send_video),
            ("Documento", send_document)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            success = test_func()
            results.append((test_name, success))
            
            if success:
                print(f"✅ {test_name}: SUCESSO")
            else:
                print(f"❌ {test_name}: FALHOU")
            
            # Aguarda entre os testes
            import time
            time.sleep(2)
        
        # Resumo final
        print("\n" + "="*50)
        print("📊 RESUMO DOS TESTES")
        print("="*50)
        
        success_count = sum(1 for _, success in results if success)
        total_tests = len(results)
        
        for test_name, success in results:
            status_icon = "✅" if success else "❌"
            print(f"{status_icon} {test_name}")
        
        print(f"\n🎯 Resultado: {success_count}/{total_tests} testes bem-sucedidos")
        
        if success_count == total_tests:
            print("\n🎉 PARABÉNS! Todos os testes passaram!")
            print("✅ A Evolution API está funcionando perfeitamente para envio de mídia!")
            print("🚀 Você pode usar a Evolution API como alternativa ao WAHA Core.")
        elif success_count > 0:
            print(f"\n⚠️ {success_count} de {total_tests} testes passaram.")
            print("🔧 Verifique os erros acima para os testes que falharam.")
        else:
            print("\n❌ Todos os testes falharam.")
            print("🔧 Verifique a configuração da Evolution API.")
            
    elif status == 'connecting':
        print("⏳ Instância ainda está conectando...")
        print("\n📱 INSTRUÇÕES PARA CONECTAR:")
        print("1. Acesse http://localhost:8080 no seu navegador")
        print("2. Faça login com a API Key: evolution-api-key-2025")
        print("3. Encontre a instância 'whatsapp-sender'")
        print("4. Escaneie o QR Code com seu WhatsApp")
        print("5. Execute este script novamente após conectar")
        
    else:
        print(f"❌ Status da instância: {status}")
        print("🔧 Verifique se a Evolution API está funcionando corretamente.")

if __name__ == "__main__":
    main()