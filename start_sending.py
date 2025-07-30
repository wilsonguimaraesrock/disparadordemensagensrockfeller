#!/usr/bin/env python3
"""
Script para iniciar o envio de mensagens para contatos selecionados
"""

import requests
import json

def start_sending():
    """Inicia o envio de mensagens para todos os contatos válidos"""
    url = "http://127.0.0.1:5001/api/start_sending"
    
    # Dados para envio - enviando para todos os contatos válidos
    # Não enviando contact_ids para usar todos os contatos válidos
    data = {}
    
    try:
        print("🚀 Iniciando envio de mensagens...")
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Envio iniciado com sucesso!")
                print(f"📊 Total de mensagens: {result.get('total_messages', 'N/A')}")
                print(f"👥 Contatos selecionados: {result.get('selected_contacts', 'N/A')}")
                print("\n🔍 Acompanhe o progresso na interface web:")
                print("🌐 http://127.0.0.1:5001")
            else:
                print(f"❌ Erro: {result.get('error', 'Erro desconhecido')}")
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor")
        print("🔍 Verifique se o servidor está rodando em http://127.0.0.1:5001")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    start_sending()