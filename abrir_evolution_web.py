#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para abrir a interface web da Evolution API
"""

import webbrowser
import time
import requests

def verificar_evolution_api():
    """Verifica se a Evolution API está rodando"""
    try:
        response = requests.get("http://localhost:8080", timeout=5)
        if response.status_code == 200:
            print("✅ Evolution API está rodando")
            return True
        else:
            print(f"❌ Evolution API retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com Evolution API: {e}")
        return False

def main():
    print("🌐 ABRINDO INTERFACE WEB DA EVOLUTION API")
    print("="*50)
    
    # Verificar se a API está rodando
    if not verificar_evolution_api():
        print("\n⚠️  A Evolution API não está acessível.")
        print("Verifique se o Docker está rodando:")
        print("   docker ps")
        print("\nSe necessário, inicie os containers:")
        print("   docker-compose up -d")
        return
    
    # Abrir no navegador
    url = "http://localhost:8080"
    print(f"\n🚀 Abrindo {url} no navegador...")
    
    try:
        webbrowser.open(url)
        print("✅ Navegador aberto com sucesso!")
        
        print("\n📋 INSTRUÇÕES PARA CONECTAR AO WHATSAPP:")
        print("1. Na interface web, encontre a instância 'whatsapp-sender-v2'")
        print("2. Clique em 'Connect' ou 'Conectar'")
        print("3. Escaneie o QR Code com seu WhatsApp")
        print("4. Aguarde a conexão ser estabelecida")
        print("\n⚠️  IMPORTANTE: Mantenha esta janela aberta durante o processo")
        
        # Aguardar um pouco
        print("\n⏳ Aguardando 10 segundos para você conectar...")
        time.sleep(10)
        
        # Verificar status da conexão
        print("\n🔍 Verificando status da conexão...")
        try:
            response = requests.get(
                "http://localhost:8080/instance/connectionState/whatsapp-sender-v2",
                headers={'apikey': 'evolution-api-key-2025'},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                state = data.get('instance', {}).get('state', 'unknown')
                print(f"Status atual: {state}")
                
                if state == 'open':
                    print("🎉 Conexão estabelecida com sucesso!")
                    print("Agora você pode testar o envio de mensagens.")
                elif state == 'connecting':
                    print("⏳ Ainda conectando... Escaneie o QR Code se ainda não fez.")
                else:
                    print(f"⚠️  Status: {state}")
            else:
                print(f"❌ Erro ao verificar status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro ao verificar status: {e}")
            
    except Exception as e:
        print(f"❌ Erro ao abrir navegador: {e}")
        print(f"\nTente abrir manualmente: {url}")

if __name__ == "__main__":
    main()