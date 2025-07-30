#!/usr/bin/env python3
"""
Script de teste para verificar o envio de mídia via WAHA
"""

import requests
import json
import os
import mimetypes
from pathlib import Path

def test_waha_media_send():
    """Testa o envio de mídia via WAHA com debug detalhado"""
    
    # Configurações WAHA
    base_url = "http://localhost:3000"
    api_key = "waha-key-2025"
    session_name = "default"
    
    # Número de teste (use um número válido)
    numero_teste = "5547996083460"  # Remover + para teste
    
    print("🧪 Testando envio de mídia via WAHA")
    print("=" * 50)
    
    # 1. Verificar se a sessão está ativa
    print("\n1. Verificando status da sessão...")
    try:
        session_url = f"{base_url}/api/sessions/{session_name}"
        headers = {
            'X-Api-Key': api_key,
            'Content-Type': 'application/json'
        }
        
        response = requests.get(session_url, headers=headers)
        print(f"   Status da sessão: {response.status_code}")
        if response.status_code == 200:
            session_data = response.json()
            print(f"   Dados da sessão: {json.dumps(session_data, indent=2)}")
            
            # Verificar se está autenticado
            status = session_data.get('status', 'unknown')
            print(f"   Status de autenticação: {status}")
            
            if status != 'WORKING':
                print("   ⚠️  Sessão não está em estado WORKING. Mídia pode falhar.")
        else:
            print(f"   ❌ Erro ao verificar sessão: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Exceção ao verificar sessão: {e}")
        return
    
    # 2. Procurar arquivo de mídia para teste
    print("\n2. Procurando arquivo de mídia para teste...")
    
    # Procurar por arquivos de imagem comuns
    possible_files = [
        "test_image.jpg",
        "test_image.png", 
        "sample.jpg",
        "sample.png",
        "image.jpg",
        "image.png"
    ]
    
    test_file = None
    for filename in possible_files:
        if os.path.exists(filename):
            test_file = filename
            break
    
    if not test_file:
        # Criar um arquivo de teste simples
        print("   📝 Criando arquivo de teste...")
        test_file = "test_media.txt"
        with open(test_file, 'w') as f:
            f.write("Este é um arquivo de teste para envio de mídia via WAHA.")
    
    print(f"   📁 Usando arquivo: {test_file}")
    
    # 3. Determinar endpoint baseado no tipo de arquivo
    print("\n3. Determinando endpoint...")
    
    mime_type, _ = mimetypes.guess_type(test_file)
    print(f"   MIME Type: {mime_type}")
    
    if mime_type:
        if mime_type.startswith('image/'):
            endpoint = "/api/sendImage"
        elif mime_type.startswith('video/'):
            endpoint = "/api/sendVideo"
        elif mime_type.startswith('audio/'):
            endpoint = "/api/sendVoice"
        else:
            endpoint = "/api/sendFile"
    else:
        endpoint = "/api/sendFile"
    
    print(f"   Endpoint: {endpoint}")
    
    # 4. Testar envio de mídia
    print("\n4. Testando envio de mídia...")
    
    url = f"{base_url}{endpoint}"
    print(f"   URL completa: {url}")
    
    try:
        with open(test_file, 'rb') as file:
            files = {'file': file}
            data = {
                'chatId': f"{numero_teste}@c.us",
                'caption': 'Teste de envio de mídia via WAHA',
                'session': session_name
            }
            
            # Headers sem Content-Type para upload
            headers = {
                'X-Api-Key': api_key
            }
            
            print(f"   📤 Enviando arquivo...")
            print(f"   Data: {data}")
            print(f"   Headers: {headers}")
            
            response = requests.post(url, files=files, data=data, headers=headers, timeout=60)
            
            print(f"   📊 Status Code: {response.status_code}")
            print(f"   📊 Response Headers: {dict(response.headers)}")
            
            try:
                response_json = response.json()
                print(f"   📊 Response JSON: {json.dumps(response_json, indent=2)}")
            except:
                print(f"   📊 Response Text: {response.text}")
            
            if response.status_code in [200, 201]:
                print("   ✅ Mídia enviada com sucesso!")
            else:
                print(f"   ❌ Falha no envio: HTTP {response.status_code}")
                
                # Tentar diagnosticar o erro
                if response.status_code == 401:
                    print("   🔍 Erro 401: Problema de autenticação")
                    print("   💡 Verifique se a API Key está correta")
                elif response.status_code == 500:
                    print("   🔍 Erro 500: Erro interno do servidor WAHA")
                    print("   💡 Verifique se a sessão está autenticada")
                    print("   💡 Verifique os logs do WAHA")
                elif response.status_code == 422:
                    print("   🔍 Erro 422: Dados inválidos")
                    print("   💡 Verifique o formato dos dados enviados")
                
    except Exception as e:
        print(f"   ❌ Exceção durante envio: {e}")
    
    # 5. Testar envio de texto para comparação
    print("\n5. Testando envio de texto para comparação...")
    
    try:
        text_url = f"{base_url}/api/sendText"
        payload = {
            "chatId": f"{numero_teste}@c.us",
            "text": "Teste de mensagem de texto via WAHA",
            "session": session_name
        }
        
        headers = {
            'X-Api-Key': api_key,
            'Content-Type': 'application/json'
        }
        
        print(f"   📤 Enviando texto...")
        response = requests.post(text_url, json=payload, headers=headers)
        
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print("   ✅ Texto enviado com sucesso!")
        else:
            print(f"   ❌ Falha no envio de texto: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exceção durante envio de texto: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Teste concluído")

if __name__ == "__main__":
    test_waha_media_send()