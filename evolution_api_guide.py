#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guia Completo - Evolution API para Envio de Mídia
Este script demonstra como usar a Evolution API como alternativa ao WAHA Core
"""

import requests
import json
import time
from typing import Dict, Any, Optional

class EvolutionAPI:
    """Cliente para Evolution API"""
    
    def __init__(self, base_url: str = "http://localhost:8080", api_key: str = "evolution-api-key-2025"):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'apikey': self.api_key
        }
    
    def create_instance(self, instance_name: str) -> Dict[str, Any]:
        """Cria uma nova instância do WhatsApp"""
        data = {
            "instanceName": instance_name,
            "integration": "WHATSAPP-BAILEYS",
            "qrcode": True,
            "webhookUrl": "",
            "webhookByEvents": False,
            "webhookBase64": False,
            "rejectCall": False,
            "msgCall": "",
            "groupsIgnore": False,
            "alwaysOnline": False,
            "readMessages": False,
            "readStatus": False,
            "syncFullHistory": False
        }
        
        response = requests.post(
            f"{self.base_url}/instance/create",
            json=data,
            headers=self.headers
        )
        
        return {
            'status_code': response.status_code,
            'data': response.json() if response.status_code in [200, 201] else response.text
        }
    
    def get_instance_status(self, instance_name: str) -> str:
        """Obtém o status da instância"""
        try:
            response = requests.get(
                f"{self.base_url}/instance/connectionState/{instance_name}",
                headers={'apikey': self.api_key}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('instance', {}).get('state', 'unknown')
            else:
                return 'error'
        except Exception:
            return 'error'
    
    def send_text(self, instance_name: str, phone: str, message: str) -> Dict[str, Any]:
        """Envia mensagem de texto"""
        data = {
            "number": phone,
            "text": message
        }
        
        response = requests.post(
            f"{self.base_url}/message/sendText/{instance_name}",
            json=data,
            headers=self.headers
        )
        
        return {
            'status_code': response.status_code,
            'success': response.status_code == 201,
            'data': response.json() if response.status_code == 201 else response.text
        }
    
    def send_image(self, instance_name: str, phone: str, image_url: str, caption: str = "") -> Dict[str, Any]:
        """Envia imagem"""
        data = {
            "number": phone,
            "mediaMessage": {
                "mediatype": "image",
                "media": image_url,
                "caption": caption
            }
        }
        
        response = requests.post(
            f"{self.base_url}/message/sendMedia/{instance_name}",
            json=data,
            headers=self.headers
        )
        
        return {
            'status_code': response.status_code,
            'success': response.status_code == 201,
            'data': response.json() if response.status_code == 201 else response.text
        }
    
    def send_video(self, instance_name: str, phone: str, video_url: str, caption: str = "") -> Dict[str, Any]:
        """Envia vídeo"""
        data = {
            "number": phone,
            "mediaMessage": {
                "mediatype": "video",
                "media": video_url,
                "caption": caption
            }
        }
        
        response = requests.post(
            f"{self.base_url}/message/sendMedia/{instance_name}",
            json=data,
            headers=self.headers
        )
        
        return {
            'status_code': response.status_code,
            'success': response.status_code == 201,
            'data': response.json() if response.status_code == 201 else response.text
        }
    
    def send_document(self, instance_name: str, phone: str, document_url: str, filename: str, caption: str = "") -> Dict[str, Any]:
        """Envia documento"""
        data = {
            "number": phone,
            "mediaMessage": {
                "mediatype": "document",
                "media": document_url,
                "fileName": filename,
                "caption": caption
            }
        }
        
        response = requests.post(
            f"{self.base_url}/message/sendMedia/{instance_name}",
            json=data,
            headers=self.headers
        )
        
        return {
            'status_code': response.status_code,
            'success': response.status_code == 201,
            'data': response.json() if response.status_code == 201 else response.text
        }
    
    def send_audio(self, instance_name: str, phone: str, audio_url: str) -> Dict[str, Any]:
        """Envia áudio"""
        data = {
            "number": phone,
            "mediaMessage": {
                "mediatype": "audio",
                "media": audio_url
            }
        }
        
        response = requests.post(
            f"{self.base_url}/message/sendMedia/{instance_name}",
            json=data,
            headers=self.headers
        )
        
        return {
            'status_code': response.status_code,
            'success': response.status_code == 201,
            'data': response.json() if response.status_code == 201 else response.text
        }

def print_setup_instructions():
    """Imprime instruções de configuração"""
    print("\n" + "="*60)
    print("🚀 GUIA DE CONFIGURAÇÃO - EVOLUTION API")
    print("="*60)
    
    print("\n📋 PRÉ-REQUISITOS:")
    print("✅ Docker e Docker Compose instalados")
    print("✅ Evolution API rodando na porta 8080")
    print("✅ API Key configurada: evolution-api-key-2025")
    
    print("\n🔧 PASSOS PARA CONECTAR:")
    print("1. 🌐 Acesse http://localhost:8080 no navegador")
    print("2. 🔑 Use a API Key: evolution-api-key-2025")
    print("3. 📱 Encontre a instância 'whatsapp-sender'")
    print("4. 📷 Escaneie o QR Code com seu WhatsApp")
    print("5. ✅ Aguarde a conexão ser estabelecida")
    
    print("\n💡 DICAS:")
    print("• O QR Code pode demorar alguns segundos para aparecer")
    print("• Mantenha o WhatsApp conectado no celular")
    print("• Use um número de teste para os primeiros envios")
    
    print("\n🔄 APÓS CONECTAR:")
    print("• Execute este script novamente")
    print("• Os testes de mídia serão executados automaticamente")
    print("• Verifique as mensagens no WhatsApp de destino")

def demonstrate_usage():
    """Demonstra como usar a Evolution API"""
    print("\n" + "="*60)
    print("📝 EXEMPLO DE USO - EVOLUTION API")
    print("="*60)
    
    # Inicializa o cliente
    api = EvolutionAPI()
    instance_name = "whatsapp-sender"
    test_phone = "5547996083460"  # Substitua pelo seu número
    
    # Verifica status
    status = api.get_instance_status(instance_name)
    print(f"\n📱 Status da instância: {status}")
    
    if status == 'open':
        print("\n✅ Instância conectada! Executando demonstração...")
        
        # Exemplo 1: Texto
        print("\n📝 Enviando texto...")
        result = api.send_text(
            instance_name, 
            test_phone, 
            "🤖 Olá! Esta é uma mensagem de teste da Evolution API.\n\n✅ A API está funcionando perfeitamente!"
        )
        print(f"Resultado: {'✅ Sucesso' if result['success'] else '❌ Falhou'}")
        
        time.sleep(2)
        
        # Exemplo 2: Imagem
        print("\n🖼️ Enviando imagem...")
        result = api.send_image(
            instance_name,
            test_phone,
            "https://github.com/devlikeapro/waha/raw/core/examples/dev.likeapro.jpg",
            "🖼️ Imagem de teste enviada via Evolution API!"
        )
        print(f"Resultado: {'✅ Sucesso' if result['success'] else '❌ Falhou'}")
        
        time.sleep(2)
        
        # Exemplo 3: Vídeo
        print("\n🎥 Enviando vídeo...")
        result = api.send_video(
            instance_name,
            test_phone,
            "https://github.com/devlikeapro/waha/raw/core/examples/video.mp4",
            "🎥 Vídeo de teste enviado via Evolution API!"
        )
        print(f"Resultado: {'✅ Sucesso' if result['success'] else '❌ Falhou'}")
        
        time.sleep(2)
        
        # Exemplo 4: Documento
        print("\n📄 Enviando documento...")
        result = api.send_document(
            instance_name,
            test_phone,
            "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            "teste_evolution.pdf",
            "📄 Documento de teste enviado via Evolution API!"
        )
        print(f"Resultado: {'✅ Sucesso' if result['success'] else '❌ Falhou'}")
        
        print("\n🎉 Demonstração concluída!")
        print("✅ A Evolution API pode substituir o WAHA Core para envio de mídia.")
        
    elif status == 'connecting':
        print("\n⏳ Instância ainda conectando...")
        print_setup_instructions()
        
    else:
        print(f"\n❌ Status inesperado: {status}")
        print("🔧 Verifique se a Evolution API está rodando corretamente.")

def show_code_examples():
    """Mostra exemplos de código"""
    print("\n" + "="*60)
    print("💻 EXEMPLOS DE CÓDIGO")
    print("="*60)
    
    print("\n🔧 Inicialização:")
    print("```python")
    print("from evolution_api_guide import EvolutionAPI")
    print("")
    print("# Inicializar cliente")
    print("api = EvolutionAPI()")
    print("instance_name = 'whatsapp-sender'")
    print("phone = '5547996083460'")
    print("```")
    
    print("\n📝 Enviar Texto:")
    print("```python")
    print("result = api.send_text(")
    print("    instance_name,")
    print("    phone,")
    print("    'Sua mensagem aqui'")
    print(")")
    print("```")
    
    print("\n🖼️ Enviar Imagem:")
    print("```python")
    print("result = api.send_image(")
    print("    instance_name,")
    print("    phone,")
    print("    'https://exemplo.com/imagem.jpg',")
    print("    'Legenda da imagem'")
    print(")")
    print("```")
    
    print("\n🎥 Enviar Vídeo:")
    print("```python")
    print("result = api.send_video(")
    print("    instance_name,")
    print("    phone,")
    print("    'https://exemplo.com/video.mp4',")
    print("    'Legenda do vídeo'")
    print(")")
    print("```")
    
    print("\n📄 Enviar Documento:")
    print("```python")
    print("result = api.send_document(")
    print("    instance_name,")
    print("    phone,")
    print("    'https://exemplo.com/documento.pdf',")
    print("    'nome_arquivo.pdf',")
    print("    'Legenda do documento'")
    print(")")
    print("```")

def main():
    """Função principal"""
    print("🚀 EVOLUTION API - GUIA COMPLETO PARA ENVIO DE MÍDIA")
    print("="*60)
    print("\n🎯 Este script demonstra como usar a Evolution API")
    print("   como alternativa ao WAHA Core para envio de mídia.")
    
    while True:
        print("\n" + "="*40)
        print("📋 MENU DE OPÇÕES")
        print("="*40)
        print("1. 🔧 Ver instruções de configuração")
        print("2. 🧪 Executar demonstração (requer conexão)")
        print("3. 💻 Ver exemplos de código")
        print("4. 📱 Verificar status da instância")
        print("5. 🚪 Sair")
        
        choice = input("\n👉 Escolha uma opção (1-5): ").strip()
        
        if choice == '1':
            print_setup_instructions()
        elif choice == '2':
            demonstrate_usage()
        elif choice == '3':
            show_code_examples()
        elif choice == '4':
            api = EvolutionAPI()
            status = api.get_instance_status("whatsapp-sender")
            print(f"\n📱 Status atual: {status}")
            if status == 'open':
                print("✅ Instância conectada e pronta para uso!")
            elif status == 'connecting':
                print("⏳ Instância conectando... Aguarde ou conecte manualmente.")
            else:
                print("❌ Instância não conectada. Verifique a configuração.")
        elif choice == '5':
            print("\n👋 Até logo!")
            break
        else:
            print("\n❌ Opção inválida. Tente novamente.")
        
        input("\n⏸️ Pressione Enter para continuar...")

if __name__ == "__main__":
    main()