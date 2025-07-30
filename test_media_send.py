#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar envio de imagens e vídeos via WAHA
"""

import requests
import json
import time
import os

# Configurações do WAHA
WAHA_URL = "http://localhost:3000"
API_KEY = "waha-key-2025"
SESSION = "default"

# Número de teste (substitua pelo seu número)
TEST_PHONE = "5547996083460"  # Substitua pelo número que você quer testar
CHAT_ID = f"{TEST_PHONE}@c.us"

def check_session_status():
    """Verifica o status da sessão WAHA"""
    try:
        response = requests.get(
            f"{WAHA_URL}/api/sessions/{SESSION}",
            headers={"X-Api-Key": API_KEY}
        )
        if response.status_code == 200:
            status = response.json().get('status')
            print(f"📱 Status da sessão: {status}")
            return status == 'WORKING'
        else:
            print(f"❌ Erro ao verificar status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

def send_image_from_url():
    """Testa envio de imagem usando URL"""
    print("\n🖼️ Testando envio de imagem via URL...")
    
    data = {
        "session": SESSION,
        "chatId": CHAT_ID,
        "file": {
            "mimetype": "image/jpeg",
            "url": "https://github.com/devlikeapro/waha/raw/core/examples/dev.likeapro.jpg",
            "filename": "teste_imagem.jpg"
        },
        "caption": "🖼️ Teste de envio de imagem via WAHA\n\nSe você recebeu esta imagem, o envio de mídia está funcionando!"
    }
    
    try:
        response = requests.post(
            f"{WAHA_URL}/api/sendImage",
            json=data,
            headers={
                "Content-Type": "application/json",
                "X-Api-Key": API_KEY
            }
        )
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Imagem enviada com sucesso!")
            print(f"📧 ID da mensagem: {result.get('id', 'N/A')}")
            return True
        else:
            print(f"❌ Erro ao enviar imagem: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def send_video_from_url():
    """Testa envio de vídeo usando URL"""
    print("\n🎥 Testando envio de vídeo via URL...")
    
    data = {
        "session": SESSION,
        "chatId": CHAT_ID,
        "caption": "🎥 Teste de envio de vídeo via WAHA\n\nSe você recebeu este vídeo, o envio de mídia está funcionando perfeitamente!",
        "asNote": False,
        "file": {
            "mimetype": "video/mp4",
            "filename": "teste_video.mp4",
            "url": "https://github.com/devlikeapro/waha/raw/core/examples/video.mp4"
        },
        "convert": False
    }
    
    try:
        response = requests.post(
            f"{WAHA_URL}/api/sendVideo",
            json=data,
            headers={
                "Content-Type": "application/json",
                "X-Api-Key": API_KEY
            }
        )
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Vídeo enviado com sucesso!")
            print(f"📧 ID da mensagem: {result.get('id', 'N/A')}")
            return True
        else:
            print(f"❌ Erro ao enviar vídeo: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def send_local_image():
    """Testa envio de imagem local (se existir)"""
    print("\n🖼️ Testando envio de imagem local...")
    
    # Procura por arquivos de imagem no diretório uploads/media
    media_dir = "uploads/media"
    if not os.path.exists(media_dir):
        print(f"❌ Diretório {media_dir} não encontrado")
        return False
    
    # Procura por arquivos de imagem
    image_files = []
    for file in os.listdir(media_dir):
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            image_files.append(file)
    
    if not image_files:
        print(f"❌ Nenhuma imagem encontrada em {media_dir}")
        return False
    
    # Usa a primeira imagem encontrada
    image_file = image_files[0]
    image_path = os.path.join(media_dir, image_file)
    
    print(f"📁 Usando imagem: {image_file}")
    
    # Lê o arquivo e converte para base64
    import base64
    try:
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Determina o mimetype
        if image_file.lower().endswith('.png'):
            mimetype = "image/png"
        elif image_file.lower().endswith('.webp'):
            mimetype = "image/webp"
        else:
            mimetype = "image/jpeg"
        
        data = {
            "session": SESSION,
            "chatId": CHAT_ID,
            "file": {
                "mimetype": mimetype,
                "filename": image_file,
                "data": image_data
            },
            "caption": f"🖼️ Teste de envio de imagem local via WAHA\n\nArquivo: {image_file}\nSe você recebeu esta imagem, o envio de arquivos locais está funcionando!"
        }
        
        response = requests.post(
            f"{WAHA_URL}/api/sendImage",
            json=data,
            headers={
                "Content-Type": "application/json",
                "X-Api-Key": API_KEY
            }
        )
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Imagem local enviada com sucesso!")
            print(f"📧 ID da mensagem: {result.get('id', 'N/A')}")
            return True
        else:
            print(f"❌ Erro ao enviar imagem local: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao processar imagem local: {e}")
        return False

def main():
    print("🚀 Iniciando testes de envio de mídia via WAHA")
    print(f"📱 Número de teste: {TEST_PHONE}")
    print("="*50)
    
    # Verifica se a sessão está ativa
    if not check_session_status():
        print("❌ Sessão não está ativa. Verifique a conexão do WAHA.")
        return
    
    print("\n✅ Sessão ativa! Iniciando testes...")
    
    # Teste 1: Envio de imagem via URL
    success_image_url = send_image_from_url()
    
    if success_image_url:
        print("\n⏳ Aguardando 3 segundos antes do próximo teste...")
        time.sleep(3)
    
    # Teste 2: Envio de vídeo via URL
    success_video_url = send_video_from_url()
    
    if success_video_url:
        print("\n⏳ Aguardando 3 segundos antes do próximo teste...")
        time.sleep(3)
    
    # Teste 3: Envio de imagem local (se disponível)
    success_local_image = send_local_image()
    
    # Resumo dos resultados
    print("\n" + "="*50)
    print("📊 RESUMO DOS TESTES:")
    print(f"🖼️ Imagem via URL: {'✅ Sucesso' if success_image_url else '❌ Falhou'}")
    print(f"🎥 Vídeo via URL: {'✅ Sucesso' if success_video_url else '❌ Falhou'}")
    print(f"🖼️ Imagem local: {'✅ Sucesso' if success_local_image else '❌ Falhou'}")
    
    if success_image_url or success_video_url or success_local_image:
        print("\n🎉 Pelo menos um teste foi bem-sucedido!")
        print("\n🔧 Próximos passos:")
        print("1. ✅ Integrar envio de mídia no sistema principal")
        print("2. 📁 Implementar upload de arquivos locais")
        print("3. 🔄 Adicionar validação de tipos de arquivo")
        print("4. 📊 Implementar logs de envio de mídia")
    else:
        print("\n❌ Todos os testes falharam.")
        print("\n🔧 Soluções possíveis:")
        print("1. Verificar se o WAHA está rodando corretamente")
        print("2. Confirmar se a sessão está conectada")
        print("3. Verificar se o número de destino está correto")
        print("4. Tentar reiniciar a sessão WAHA")

if __name__ == "__main__":
    main()