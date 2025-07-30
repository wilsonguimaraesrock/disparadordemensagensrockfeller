#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitoramento em tempo real da conexão Evolution API
"""

import requests
import time
import json
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:8081"
API_KEY = "evolution-api-key-2025"
INSTANCE_NAME = "whatsapp-sender-v2"

headers = {
    'apikey': API_KEY,
    'Content-Type': 'application/json'
}

def verificar_status():
    """Verifica o status atual da instância"""
    try:
        # Status da conexão
        response = requests.get(
            f"{BASE_URL}/instance/connectionState/{INSTANCE_NAME}",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            state = data.get('instance', {}).get('state', 'unknown')
            return state
        else:
            return f"erro_{response.status_code}"
            
    except Exception as e:
        return f"erro_{str(e)}"

def verificar_instancia_detalhes():
    """Verifica detalhes da instância"""
    try:
        response = requests.get(
            f"{BASE_URL}/instance/fetchInstances",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            instances = response.json()
            for instance in instances:
                if instance.get('name') == INSTANCE_NAME:
                    return {
                        'connectionStatus': instance.get('connectionStatus'),
                        'ownerJid': instance.get('ownerJid'),
                        'profileName': instance.get('profileName'),
                        'number': instance.get('number')
                    }
        return None
        
    except Exception as e:
        return {'erro': str(e)}

def main():
    print("📱 MONITORAMENTO EVOLUTION API - CONEXÃO WHATSAPP")
    print("="*60)
    print(f"Instância: {INSTANCE_NAME}")
    print(f"URL: {BASE_URL}")
    print("\nPressione Ctrl+C para parar o monitoramento\n")
    
    status_anterior = None
    contador = 0
    
    try:
        while True:
            contador += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Verificar status
            status_atual = verificar_status()
            detalhes = verificar_instancia_detalhes()
            
            # Mostrar apenas se mudou ou a cada 10 verificações
            if status_atual != status_anterior or contador % 10 == 0:
                print(f"\n[{timestamp}] Status: {status_atual}")
                
                if detalhes and not detalhes.get('erro'):
                    print(f"   Connection Status: {detalhes.get('connectionStatus', 'N/A')}")
                    if detalhes.get('ownerJid'):
                        print(f"   Owner JID: {detalhes.get('ownerJid')}")
                    if detalhes.get('profileName'):
                        print(f"   Profile: {detalhes.get('profileName')}")
                    if detalhes.get('number'):
                        print(f"   Número: {detalhes.get('number')}")
                
                # Mensagens de status
                if status_atual == 'open':
                    print("   🎉 CONECTADO! WhatsApp está pronto para uso.")
                    if status_anterior != 'open':
                        print("   ✅ Conexão estabelecida com sucesso!")
                        print("   Agora você pode testar o envio de mensagens.")
                elif status_atual == 'connecting':
                    print("   ⏳ Conectando... Escaneie o QR Code se ainda não fez.")
                elif status_atual == 'close':
                    print("   ❌ Desconectado. Precisa escanear o QR Code.")
                elif status_atual.startswith('erro'):
                    print(f"   ⚠️  Erro na verificação: {status_atual}")
                
                status_anterior = status_atual
            else:
                # Mostrar apenas um ponto para indicar que está monitorando
                print(".", end="", flush=True)
            
            time.sleep(3)  # Verificar a cada 3 segundos
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoramento interrompido pelo usuário.")
        print(f"Status final: {status_atual}")
        
        if status_atual == 'open':
            print("\n🎉 WhatsApp está conectado e pronto para uso!")
            print("Você pode agora:")
            print("1. Testar o envio de mensagens")
            print("2. Executar o script de teste de mídia")
            print("3. Usar o sistema de envio em lote")
        else:
            print("\n⚠️  WhatsApp não está conectado.")
            print("Para conectar:")
            print("1. Acesse http://localhost:8081")
            print("2. Encontre a instância 'whatsapp-sender-v2'")
            print("3. Clique em Connect e escaneie o QR Code")
    
    except Exception as e:
        print(f"\n❌ Erro no monitoramento: {e}")

if __name__ == "__main__":
    main()