#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para configurar Evolution API como alternativa para envio de mídia
"""

import subprocess
import requests
import time
import json
import os

# Configurações da Evolution API
EVOLUTION_PORT = 8080
EVOLUTION_URL = f"http://localhost:{EVOLUTION_PORT}"
API_KEY = "evolution-api-key-2025"
INSTANCE_NAME = "whatsapp-sender"

def check_docker():
    """Verifica se o Docker está instalado e rodando"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker encontrado: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker não encontrado")
            return False
    except FileNotFoundError:
        print("❌ Docker não está instalado")
        return False

def stop_existing_evolution():
    """Para container Evolution API existente se houver"""
    try:
        print("🔄 Verificando containers Evolution API existentes...")
        result = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=evolution-api', '--format', '{{.Names}}'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            print("🛑 Parando container Evolution API existente...")
            subprocess.run(['docker', 'stop', 'evolution-api'], capture_output=True)
            subprocess.run(['docker', 'rm', 'evolution-api'], capture_output=True)
            print("✅ Container anterior removido")
        else:
            print("ℹ️ Nenhum container Evolution API encontrado")
    except Exception as e:
        print(f"⚠️ Erro ao verificar containers: {e}")

def start_evolution_api():
    """Inicia o container da Evolution API"""
    print("🚀 Iniciando Evolution API...")
    
    docker_cmd = [
        'docker', 'run', '-d',
        '--name', 'evolution-api',
        '-p', f'{EVOLUTION_PORT}:8080',
        '-e', f'AUTHENTICATION_API_KEY={API_KEY}',
        '-e', 'AUTHENTICATION_EXPOSE_IN_FETCH_INSTANCES=true',
        '-e', 'QRCODE_LIMIT=30',
        '-e', 'WEBSOCKET_ENABLED=false',
        '-e', 'DATABASE_ENABLED=false',
        '-e', 'DATABASE_PROVIDER=',
        '-e', 'CACHE_REDIS_ENABLED=false',
        '-e', 'CACHE_LOCAL_ENABLED=true',
        'atendai/evolution-api:latest'
    ]
    
    try:
        result = subprocess.run(docker_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Evolution API iniciada com sucesso!")
            print(f"📱 Container ID: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Erro ao iniciar Evolution API: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro ao executar Docker: {e}")
        return False

def wait_for_api():
    """Aguarda a API ficar disponível"""
    print("⏳ Aguardando Evolution API ficar disponível...")
    
    for i in range(30):  # Tenta por 30 segundos
        try:
            response = requests.get(f"{EVOLUTION_URL}/manager/instances", 
                                  headers={'apikey': API_KEY},
                                  timeout=5)
            if response.status_code == 200:
                print("✅ Evolution API está respondendo!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"⏳ Tentativa {i+1}/30...")
        time.sleep(1)
    
    print("❌ Evolution API não respondeu no tempo esperado")
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
            f"{EVOLUTION_URL}/manager/instances",
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
            if 'base64' in result:
                # Salva o QR Code como imagem
                import base64
                qr_data = result['base64'].split(',')[1]  # Remove o prefixo data:image/png;base64,
                
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
            return None
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def create_test_script():
    """Cria script de teste para Evolution API"""
    test_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para Evolution API - Envio de Mídia
"""

import requests
import json

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

def send_text_message():
    """Testa envio de mensagem de texto"""
    print("\n📝 Testando envio de texto...")
    
    data = {
        "number": TEST_PHONE,
        "text": "🤖 Teste Evolution API\\n\\nSe você recebeu esta mensagem, a Evolution API está funcionando!"
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
            "caption": "🖼️ Teste de imagem via Evolution API\\n\\nSe você recebeu esta imagem, o envio de mídia está funcionando!"
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
            "caption": "🎥 Teste de vídeo via Evolution API\\n\\nSe você recebeu este vídeo, o envio de mídia está funcionando perfeitamente!"
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
    
    if not check_connection():
        print("❌ Instância não está conectada. Execute o setup primeiro.")
        return
    
    print("✅ Instância conectada! Iniciando testes...")
    
    # Testes
    send_text_message()
    time.sleep(2)
    
    send_image()
    time.sleep(2)
    
    send_video()
    
    print("\n🎉 Testes concluídos!")

if __name__ == "__main__":
    import time
    main()
'''
    
    with open('test_evolution_api.py', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("✅ Script de teste criado: 'test_evolution_api.py'")

def main():
    print("🚀 Configurando Evolution API para envio de mídia")
    print("="*60)
    
    # Verifica Docker
    if not check_docker():
        print("\n❌ Docker é necessário para continuar.")
        print("📥 Instale o Docker em: https://www.docker.com/get-started")
        return
    
    # Para container existente
    stop_existing_evolution()
    
    # Inicia Evolution API
    if not start_evolution_api():
        return
    
    # Aguarda API ficar disponível
    if not wait_for_api():
        return
    
    # Cria instância
    if not create_instance():
        return
    
    # Aguarda um pouco para a instância inicializar
    print("⏳ Aguardando instância inicializar...")
    time.sleep(5)
    
    # Obtém QR Code
    if get_qr_code():
        print("\n" + "="*60)
        print("✅ EVOLUTION API CONFIGURADA COM SUCESSO!")
        print("\n📋 Informações importantes:")
        print(f"🌐 URL da API: {EVOLUTION_URL}")
        print(f"🔑 API Key: {API_KEY}")
        print(f"📱 Nome da Instância: {INSTANCE_NAME}")
        print(f"🖼️ QR Code salvo em: evolution_qr_code.png")
        
        print("\n📱 PRÓXIMOS PASSOS:")
        print("1. Abra o arquivo 'evolution_qr_code.png'")
        print("2. Escaneie o QR Code com seu WhatsApp")
        print("3. Aguarde a conexão ser estabelecida")
        print("4. Execute 'python3 test_evolution_api.py' para testar")
        
        # Cria script de teste
        create_test_script()
        
        print("\n🔧 COMANDOS ÚTEIS:")
        print(f"📊 Verificar status: curl -H 'apikey: {API_KEY}' {EVOLUTION_URL}/instance/connectionState/{INSTANCE_NAME}")
        print(f"🛑 Parar container: docker stop evolution-api")
        print(f"🚀 Iniciar container: docker start evolution-api")
        
    else:
        print("❌ Falha ao obter QR Code")

if __name__ == "__main__":
    main()