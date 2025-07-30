#!/usr/bin/env python3
"""
Teste de Integração da Evolution API com o Sistema de Envio
Este script testa a integração da Evolution API com a aplicação existente
"""

import os
import sys
import json
import time
from pathlib import Path

# Adicionar o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_sender import WhatsAppAPISender
from utils import setup_logging, load_config

def test_evolution_api_integration():
    """
    Testa a integração da Evolution API com o sistema existente
    """
    print("🚀 Iniciando teste de integração da Evolution API...\n")
    
    # Configurar logging
    setup_logging()
    
    try:
        # Carregar configuração da Evolution API
        config_file = 'config_evolution.json'
        if not os.path.exists(config_file):
            print(f"❌ Arquivo de configuração não encontrado: {config_file}")
            print("💡 Certifique-se de que o arquivo config_evolution.json existe")
            return False
        
        print(f"📋 Carregando configuração de {config_file}...")
        config = load_config(config_file)
        print(f"✅ Configuração carregada: {config['provider']} - {config['base_url']}")
        
        # Inicializar o sender
        print("\n🔧 Inicializando WhatsApp API Sender...")
        sender = WhatsAppAPISender(config)
        print("✅ Sender inicializado com sucesso")
        
        # Número de teste (substitua pelo seu número)
        numero_teste = input("\n📱 Digite o número de teste (com DDI, ex: +5521999998888): ").strip()
        if not numero_teste:
            print("❌ Número não fornecido")
            return False
        
        print(f"\n📞 Número de teste: {numero_teste}")
        
        # Teste 1: Envio de mensagem de texto
        print("\n" + "="*50)
        print("📝 TESTE 1: Envio de mensagem de texto")
        print("="*50)
        
        mensagem_teste = "🤖 Teste de integração da Evolution API com o sistema de envio em massa! ✅"
        print(f"Mensagem: {mensagem_teste}")
        
        print("\n🚀 Enviando mensagem de texto...")
        resultado_texto = sender.send_message(numero_teste, mensagem_teste)
        
        if resultado_texto:
            print("✅ Mensagem de texto enviada com sucesso!")
        else:
            print("❌ Falha no envio da mensagem de texto")
        
        # Aguardar entre testes
        print("\n⏳ Aguardando 5 segundos antes do próximo teste...")
        time.sleep(5)
        
        # Teste 2: Envio de imagem (se existir)
        print("\n" + "="*50)
        print("🖼️ TESTE 2: Envio de imagem")
        print("="*50)
        
        # Procurar por arquivos de imagem no diretório
        imagem_teste = None
        extensoes_imagem = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        
        for arquivo in os.listdir('.'):
            if any(arquivo.lower().endswith(ext) for ext in extensoes_imagem):
                imagem_teste = arquivo
                break
        
        if imagem_teste and os.path.exists(imagem_teste):
            print(f"📁 Arquivo de imagem encontrado: {imagem_teste}")
            mensagem_imagem = "📸 Teste de envio de imagem via Evolution API!"
            
            print("\n🚀 Enviando imagem...")
            resultado_imagem = sender.send_message(numero_teste, mensagem_imagem, imagem_teste)
            
            if resultado_imagem:
                print("✅ Imagem enviada com sucesso!")
            else:
                print("❌ Falha no envio da imagem")
        else:
            print("⚠️ Nenhuma imagem encontrada no diretório para teste")
            print("💡 Adicione uma imagem (.jpg, .png, etc.) no diretório para testar o envio de mídia")
        
        # Exibir log de resultados
        print("\n" + "="*50)
        print("📊 RESULTADOS DOS TESTES")
        print("="*50)
        
        log_file = sender.get_log_filename()
        if os.path.exists(log_file):
            print(f"📋 Arquivo de log: {log_file}")
            print("\n📝 Últimas entradas do log:")
            
            with open(log_file, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
                for linha in linhas[-5:]:  # Últimas 5 linhas
                    print(f"   {linha.strip()}")
        
        print("\n" + "="*50)
        print("🎯 RESUMO DO TESTE")
        print("="*50)
        print(f"Provider: {config['provider']}")
        print(f"Base URL: {config['base_url']}")
        print(f"Instance ID: {config['instance_id']}")
        print(f"Número testado: {numero_teste}")
        print(f"Texto enviado: {'✅' if resultado_texto else '❌'}")
        if imagem_teste:
            print(f"Imagem enviada: {'✅' if resultado_imagem else '❌'}")
        
        return resultado_texto
        
    except Exception as e:
        print(f"💥 Erro durante o teste: {e}")
        return False

def verificar_evolution_api():
    """
    Verifica se a Evolution API está rodando
    """
    import requests
    
    try:
        print("🔍 Verificando se a Evolution API está rodando...")
        response = requests.get('http://localhost:8080', timeout=5)
        
        if response.status_code == 200:
            print("✅ Evolution API está rodando!")
            return True
        else:
            print(f"⚠️ Evolution API respondeu com status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Evolution API não está rodando ou não está acessível")
        print("💡 Execute: docker-compose up -d")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar Evolution API: {e}")
        return False

def main():
    """
    Função principal
    """
    print("🔥 TESTE DE INTEGRAÇÃO - EVOLUTION API")
    print("="*60)
    
    # Verificar se a Evolution API está rodando
    if not verificar_evolution_api():
        print("\n❌ Não é possível continuar sem a Evolution API")
        return
    
    # Executar teste de integração
    sucesso = test_evolution_api_integration()
    
    print("\n" + "="*60)
    if sucesso:
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("✅ A Evolution API está integrada e funcionando")
        print("\n💡 Próximos passos:")
        print("   1. Atualize o config.json para usar 'evolution-api'")
        print("   2. Configure sua planilha de contatos")
        print("   3. Execute o envio em massa com main.py")
    else:
        print("❌ TESTE FALHOU")
        print("\n🔧 Verifique:")
        print("   1. Se a Evolution API está rodando (docker-compose up -d)")
        print("   2. Se a instância 'whatsapp-sender' está conectada")
        print("   3. Se a chave de API está correta")
    
    print("="*60)

if __name__ == "__main__":
    main()