#!/usr/bin/env python3
import requests
import json

def test_send_message():
    """Testa o envio de mensagem do WAHA usando o endpoint correto"""
    
    base_url = 'http://localhost:3000/api'
    headers = {
        'X-Api-Key': 'waha-key-2025',
        'Content-Type': 'application/json'
    }
    
    # Número de teste (substitua pelo seu próprio número)
    test_number = input("Digite seu número de WhatsApp (formato: 5511999999999): ")
    
    if not test_number:
        print("❌ Número não fornecido")
        return
    
    # Dados da mensagem - formato correto para WAHA Core
    message_data = {
        "session": "default",
        "chatId": f"{test_number}@c.us",
        "text": "🤖 Teste de conexão WAHA\n\nSe você recebeu esta mensagem, o WAHA está funcionando perfeitamente!"
    }
    
    try:
        print(f"📤 Enviando mensagem de teste para {test_number}...")
        print(f"📋 Dados da mensagem: {json.dumps(message_data, indent=2)}")
        
        response = requests.post(
            f'{base_url}/sendText',
            headers=headers,
            json=message_data
        )
        
        print(f"📊 Status da resposta: {response.status_code}")
        print(f"📄 Resposta completa: {response.text}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Mensagem enviada com sucesso!")
            print(f"📧 ID da mensagem: {result.get('id', 'N/A')}")
            print("\n🎉 WAHA está funcionando perfeitamente!")
            return True
            
        elif response.status_code == 400:
            print("❌ Erro 400: Verifique o formato do número")
            print("Formato correto: 5511999999999 (código do país + DDD + número)")
            
        elif response.status_code == 404:
            print("❌ Erro 404: Endpoint não encontrado")
            print("Verifique se a sessão está ativa")
            
        else:
            print(f"❌ Erro ao enviar mensagem: {response.status_code}")
            
        return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def check_session_status():
    """Verifica o status da sessão antes de enviar mensagem"""
    
    base_url = 'http://localhost:3000/api'
    headers = {'X-Api-Key': 'waha-key-2025'}
    
    try:
        print("🔍 Verificando status da sessão...")
        response = requests.get(f'{base_url}/sessions/default', headers=headers)
        
        if response.status_code == 200:
            session_data = response.json()
            status = session_data.get('status')
            print(f"✅ Status da sessão: {status}")
            
            if status == 'WORKING':
                print("🎉 Sessão está ativa e pronta para enviar mensagens!")
                return True
            elif status == 'SCAN_QR_CODE':
                print("⚠️ QR code ainda precisa ser escaneado")
                return False
            elif status == 'STARTING':
                print("⏳ Sessão ainda está iniciando...")
                return False
            else:
                print(f"❌ Status inesperado: {status}")
                return False
        else:
            print(f"❌ Erro ao verificar sessão: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Teste de Envio de Mensagem WAHA Core")
    print("=" * 45)
    
    # Primeiro verifica o status da sessão
    if check_session_status():
        print("\n" + "=" * 45)
        print("📤 Teste de Envio de Mensagem")
        print("=" * 45)
        
        # Testa envio de mensagem
        success = test_send_message()
        
        if success:
            print("\n🎯 Próximos passos:")
            print("1. ✅ WAHA está funcionando perfeitamente")
            print("2. 📱 Você pode criar scripts para envio em lote")
            print("3. 🔄 A sessão permanecerá ativa")
        else:
            print("\n🔧 Solução de problemas:")
            print("1. Verifique se o número está no formato correto")
            print("2. Certifique-se de que o WhatsApp está conectado")
            print("3. Tente reiniciar a sessão se necessário")
    else:
        print("\n❌ Sessão não está pronta. Execute o monitor_status.py primeiro.")