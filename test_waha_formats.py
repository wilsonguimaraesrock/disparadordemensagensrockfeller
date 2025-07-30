#!/usr/bin/env python3
"""
Script para testar diferentes formatos de parâmetros para a API WAHA
"""

import requests
import json
import os

def test_different_waha_formats():
    """Testa diferentes formatos de parâmetros para envio de mídia"""
    
    # Configurações WAHA
    base_url = "http://localhost:3000"
    api_key = "waha-key-2025"
    session_name = "default"
    numero_teste = "5547996083460"
    
    print("🧪 Testando diferentes formatos de parâmetros WAHA")
    print("=" * 60)
    
    # Criar arquivo de teste se não existir
    test_file = "test_media.txt"
    if not os.path.exists(test_file):
        with open(test_file, 'w') as f:
            f.write("Teste de envio de mídia via WAHA")
    
    # Teste 1: Formato atual (que está falhando)
    print("\n1️⃣ Testando formato atual (session no data)...")
    test_format_1(base_url, api_key, session_name, numero_teste, test_file)
    
    # Teste 2: Session no header
    print("\n2️⃣ Testando session no header...")
    test_format_2(base_url, api_key, session_name, numero_teste, test_file)
    
    # Teste 3: Session na URL
    print("\n3️⃣ Testando session na URL...")
    test_format_3(base_url, api_key, session_name, numero_teste, test_file)
    
    # Teste 4: Formato JSON no body
    print("\n4️⃣ Testando formato JSON no body...")
    test_format_4(base_url, api_key, session_name, numero_teste, test_file)
    
    # Teste 5: Sem session (usar default)
    print("\n5️⃣ Testando sem session (usar default)...")
    test_format_5(base_url, api_key, session_name, numero_teste, test_file)

def test_format_1(base_url, api_key, session_name, numero_teste, test_file):
    """Formato atual - session no data"""
    try:
        url = f"{base_url}/api/sendFile"
        
        with open(test_file, 'rb') as file:
            files = {'file': file}
            data = {
                'chatId': f"{numero_teste}@c.us",
                'caption': 'Teste formato 1',
                'session': session_name
            }
            
            headers = {'X-Api-Key': api_key}
            
            response = requests.post(url, files=files, data=data, headers=headers, timeout=30)
            print(f"   Status: {response.status_code}")
            
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    print(f"   Erro: {error_data.get('exception', {}).get('message', 'Erro desconhecido')}")
                except:
                    print(f"   Erro: {response.text}")
            else:
                print("   ✅ Sucesso!")
                
    except Exception as e:
        print(f"   ❌ Exceção: {e}")

def test_format_2(base_url, api_key, session_name, numero_teste, test_file):
    """Session no header"""
    try:
        url = f"{base_url}/api/sendFile"
        
        with open(test_file, 'rb') as file:
            files = {'file': file}
            data = {
                'chatId': f"{numero_teste}@c.us",
                'caption': 'Teste formato 2'
            }
            
            headers = {
                'X-Api-Key': api_key,
                'X-Session': session_name
            }
            
            response = requests.post(url, files=files, data=data, headers=headers, timeout=30)
            print(f"   Status: {response.status_code}")
            
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    print(f"   Erro: {error_data.get('exception', {}).get('message', 'Erro desconhecido')}")
                except:
                    print(f"   Erro: {response.text}")
            else:
                print("   ✅ Sucesso!")
                
    except Exception as e:
        print(f"   ❌ Exceção: {e}")

def test_format_3(base_url, api_key, session_name, numero_teste, test_file):
    """Session na URL"""
    try:
        url = f"{base_url}/api/{session_name}/sendFile"
        
        with open(test_file, 'rb') as file:
            files = {'file': file}
            data = {
                'chatId': f"{numero_teste}@c.us",
                'caption': 'Teste formato 3'
            }
            
            headers = {'X-Api-Key': api_key}
            
            response = requests.post(url, files=files, data=data, headers=headers, timeout=30)
            print(f"   Status: {response.status_code}")
            
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    print(f"   Erro: {error_data.get('exception', {}).get('message', 'Erro desconhecido')}")
                except:
                    print(f"   Erro: {response.text}")
            else:
                print("   ✅ Sucesso!")
                
    except Exception as e:
        print(f"   ❌ Exceção: {e}")

def test_format_4(base_url, api_key, session_name, numero_teste, test_file):
    """Formato JSON no body"""
    try:
        # Primeiro, fazer upload do arquivo
        upload_url = f"{base_url}/api/files/upload"
        
        with open(test_file, 'rb') as file:
            files = {'file': file}
            headers = {'X-Api-Key': api_key}
            
            upload_response = requests.post(upload_url, files=files, headers=headers, timeout=30)
            
            if upload_response.status_code == 200:
                file_data = upload_response.json()
                file_id = file_data.get('id')
                
                # Agora enviar usando o file_id
                send_url = f"{base_url}/api/sendFile"
                payload = {
                    'session': session_name,
                    'chatId': f"{numero_teste}@c.us",
                    'caption': 'Teste formato 4',
                    'file': {
                        'id': file_id
                    }
                }
                
                headers = {
                    'X-Api-Key': api_key,
                    'Content-Type': 'application/json'
                }
                
                response = requests.post(send_url, json=payload, headers=headers, timeout=30)
                print(f"   Status: {response.status_code}")
                
                if response.status_code != 200:
                    try:
                        error_data = response.json()
                        print(f"   Erro: {error_data.get('exception', {}).get('message', 'Erro desconhecido')}")
                    except:
                        print(f"   Erro: {response.text}")
                else:
                    print("   ✅ Sucesso!")
            else:
                print(f"   ❌ Falha no upload: {upload_response.status_code}")
                
    except Exception as e:
        print(f"   ❌ Exceção: {e}")

def test_format_5(base_url, api_key, session_name, numero_teste, test_file):
    """Sem session (usar default)"""
    try:
        url = f"{base_url}/api/sendFile"
        
        with open(test_file, 'rb') as file:
            files = {'file': file}
            data = {
                'chatId': f"{numero_teste}@c.us",
                'caption': 'Teste formato 5 (sem session)'
            }
            
            headers = {'X-Api-Key': api_key}
            
            response = requests.post(url, files=files, data=data, headers=headers, timeout=30)
            print(f"   Status: {response.status_code}")
            
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    print(f"   Erro: {error_data.get('exception', {}).get('message', 'Erro desconhecido')}")
                except:
                    print(f"   Erro: {response.text}")
            else:
                print("   ✅ Sucesso!")
                
    except Exception as e:
        print(f"   ❌ Exceção: {e}")

def test_text_message_for_comparison():
    """Testa envio de texto para comparação"""
    print("\n📝 Testando envio de texto para comparação...")
    
    base_url = "http://localhost:3000"
    api_key = "waha-key-2025"
    session_name = "default"
    numero_teste = "5547996083460"
    
    try:
        url = f"{base_url}/api/sendText"
        payload = {
            "chatId": f"{numero_teste}@c.us",
            "text": "Teste de comparação - mensagem de texto",
            "session": session_name
        }
        
        headers = {
            'X-Api-Key': api_key,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=payload, headers=headers)
        print(f"   Status texto: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print("   ✅ Texto enviado com sucesso!")
        else:
            print(f"   ❌ Falha no texto: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exceção no texto: {e}")

if __name__ == "__main__":
    test_different_waha_formats()
    test_text_message_for_comparison()
    
    print("\n" + "=" * 60)
    print("🏁 Testes concluídos")
    print("\n💡 Se algum formato funcionou, atualize o código principal com esse formato.")