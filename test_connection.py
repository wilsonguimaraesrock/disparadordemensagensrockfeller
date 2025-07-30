#!/usr/bin/env python3
import requests
import json

def test_waha_connection():
    """Testa a conexão do WAHA e verifica se está funcionando"""
    
    base_url = 'http://localhost:3000/api'
    headers = {'X-Api-Key': 'waha-key-2025'}
    
    try:
        # Verifica o status da sessão
        print("🔍 Verificando status da sessão...")
        response = requests.get(f'{base_url}/sessions/default', headers=headers)
        
        if response.status_code == 200:
            session_data = response.json()
            status = session_data.get('status')
            print(f"✅ Status da sessão: {status}")
            
            if status == 'WORKING':
                print("🎉 WhatsApp conectado com sucesso!")
                
                # Testa obter informações do perfil
                print("\n📱 Obtendo informações do perfil...")
                profile_response = requests.get(f'{base_url}/default/contacts/me', headers=headers)
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    print(f"✅ Perfil obtido: {profile_data.get('pushname', 'N/A')}")
                    print(f"📞 Número: {profile_data.get('id', 'N/A')}")
                else:
                    print(f"⚠️ Erro ao obter perfil: {profile_response.status_code}")
                
                # Lista contatos (primeiros 5)
                print("\n👥 Obtendo lista de contatos...")
                contacts_response = requests.get(f'{base_url}/default/contacts', headers=headers)
                
                if contacts_response.status_code == 200:
                    contacts = contacts_response.json()
                    print(f"✅ Total de contatos: {len(contacts)}")
                    
                    if contacts:
                        print("\n📋 Primeiros contatos:")
                        for i, contact in enumerate(contacts[:5]):
                            name = contact.get('name') or contact.get('pushname') or 'Sem nome'
                            number = contact.get('id', 'N/A')
                            print(f"  {i+1}. {name} - {number}")
                else:
                    print(f"⚠️ Erro ao obter contatos: {contacts_response.status_code}")
                
                print("\n🚀 WAHA está funcionando perfeitamente!")
                print("\n📝 Próximos passos:")
                print("1. Você pode agora enviar mensagens usando a API")
                print("2. Use o script de envio em lote que será criado")
                print("3. A sessão permanecerá ativa até ser desconectada")
                
            elif status == 'SCAN_QR_CODE':
                print("⚠️ QR code ainda precisa ser escaneado")
            elif status == 'STARTING':
                print("⏳ Sessão ainda está iniciando...")
            else:
                print(f"❌ Status inesperado: {status}")
        else:
            print(f"❌ Erro ao verificar sessão: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_waha_connection()