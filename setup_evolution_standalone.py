#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Evolution API - Versão Standalone (sem Docker)
Configurador automático para Evolution API local
"""

import os
import sys
import json
import time
import subprocess
import requests
from pathlib import Path


class EvolutionAPISetup:
    def __init__(self):
        self.config = {
            'base_url': 'http://localhost:8080',
            'api_key': 'evolution-api-key-2025',
            'instance_name': 'whatsapp-sender-v2'
        }
        self.evolution_path = Path('evolution-api')
    
    def verificar_node(self):
        """Verifica se Node.js está instalado"""
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ Node.js encontrado: {version}")
                return True
            else:
                print("❌ Node.js não encontrado")
                return False
        except FileNotFoundError:
            print("❌ Node.js não instalado")
            return False
    
    def verificar_npm(self):
        """Verifica se npm está instalado"""
        try:
            result = subprocess.run(['npm', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ npm encontrado: {version}")
                return True
            else:
                print("❌ npm não encontrado")
                return False
        except FileNotFoundError:
            print("❌ npm não instalado")
            return False
    
    def verificar_git(self):
        """Verifica se Git está instalado"""
        try:
            result = subprocess.run(['git', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ Git encontrado: {version}")
                return True
            else:
                print("❌ Git não encontrado")
                return False
        except FileNotFoundError:
            print("❌ Git não instalado")
            return False
    
    def clonar_evolution_api(self):
        """Clona repositório da Evolution API"""
        if self.evolution_path.exists():
            print(f"📁 Diretório {self.evolution_path} já existe")
            return True
        
        print("📥 Clonando Evolution API...")
        try:
            result = subprocess.run([
                'git', 'clone', 
                'https://github.com/EvolutionAPI/evolution-api.git',
                str(self.evolution_path)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Evolution API clonada com sucesso!")
                return True
            else:
                print(f"❌ Erro ao clonar: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def instalar_dependencias(self):
        """Instala dependências do Evolution API"""
        print("📦 Instalando dependências...")
        try:
            os.chdir(self.evolution_path)
            
            result = subprocess.run(['npm', 'install'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Dependências instaladas!")
                return True
            else:
                print(f"❌ Erro na instalação: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
        finally:
            os.chdir('..')
    
    def criar_env_file(self):
        """Cria arquivo .env para Evolution API"""
        env_content = f"""# Evolution API Configuration
AUTHENTICATION_API_KEY={self.config['api_key']}
AUTHENTICATION_EXPOSE_IN_FETCH_INSTANCES=true

# Server Configuration
SERVER_PORT=8080
SERVER_URL=http://localhost:8080

# Database (opcional - usar SQLite para simplicidade)
DATABASE_ENABLED=true
DATABASE_PROVIDER=sqlite
DATABASE_CONNECTION_URI=file:./evolution.db

# Cache (opcional)
CACHE_LOCAL_ENABLED=true
CACHE_REDIS_ENABLED=false

# Logs
LOG_LEVEL=info
LOG_COLOR=true

# QR Code
QRCODE_LIMIT=30

# WebSocket (opcional)
WEBSOCKET_ENABLED=false

# Webhook (opcional)
WEBHOOK_GLOBAL_ENABLED=false
"""
        
        env_path = self.evolution_path / '.env'
        try:
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(env_content)
            print(f"✅ Arquivo .env criado: {env_path}")
            return True
        except Exception as e:
            print(f"❌ Erro ao criar .env: {e}")
            return False
    
    def iniciar_evolution_api(self):
        """Inicia Evolution API"""
        print("🚀 Iniciando Evolution API...")
        try:
            os.chdir(self.evolution_path)
            
            # Usar npm start
            print("📡 Executando: npm start")
            print("💡 DICA: Para parar, pressione Ctrl+C")
            print("💡 ACESSO: http://localhost:8080")
            print("-" * 50)
            
            subprocess.run(['npm', 'start'], check=True)
            
        except KeyboardInterrupt:
            print("\n⚠️  Evolution API interrompida pelo usuário")
        except Exception as e:
            print(f"❌ Erro ao iniciar: {e}")
        finally:
            os.chdir('..')
    
    def verificar_api_rodando(self):
        """Verifica se a API está rodando"""
        try:
            response = requests.get(f"{self.config['base_url']}/", timeout=5)
            if response.status_code == 200:
                print(f"✅ Evolution API está rodando em {self.config['base_url']}")
                return True
            else:
                print(f"⚠️  API respondeu com status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"❌ Não foi possível conectar em {self.config['base_url']}")
            return False
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def criar_instancia(self):
        """Cria instância do WhatsApp"""
        if not self.verificar_api_rodando():
            print("❌ API não está rodando. Inicie primeiro com: python setup_evolution_standalone.py --start")
            return False
        
        print(f"📱 Criando instância: {self.config['instance_name']}")
        
        url = f"{self.config['base_url']}/instance/create"
        headers = {'apikey': self.config['api_key']}
        payload = {
            "instanceName": self.config['instance_name'],
            "token": self.config['api_key'],
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code in [200, 201]:
                result = response.json()
                print("✅ Instância criada com sucesso!")
                print(f"📋 Detalhes: {result}")
                return True
            else:
                print(f"❌ Erro HTTP {response.status_code}")
                print(f"📋 Resposta: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def conectar_instancia(self):
        """Conecta instância do WhatsApp"""
        if not self.verificar_api_rodando():
            print("❌ API não está rodando")
            return False
        
        print(f"🔗 Conectando instância: {self.config['instance_name']}")
        
        url = f"{self.config['base_url']}/instance/connect/{self.config['instance_name']}"
        headers = {'apikey': self.config['api_key']}
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Comando de conexão enviado!")
                
                if 'qrcode' in result:
                    print("📱 QR Code gerado!")
                    print("🔗 Para ver QR Code, acesse:")
                    print(f"   {self.config['base_url']}/instance/qrcode/{self.config['instance_name']}")
                    print("\n💡 INSTRUÇÕES:")
                    print("1. Abra WhatsApp no seu celular")
                    print("2. Vá em Configurações > Aparelhos conectados")
                    print("3. Toque em 'Conectar um aparelho'")
                    print("4. Escaneie o QR Code")
                
                return True
            else:
                print(f"❌ Erro HTTP {response.status_code}")
                print(f"📋 Resposta: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def atualizar_config_json(self):
        """Atualiza config.json para usar Evolution API"""
        config_path = Path('config.json')
        
        config_data = {
            "provider": "evolution-api",
            "base_url": self.config['base_url'],
            "instance_id": self.config['instance_name'],
            "token": self.config['api_key'],
            "timeout": "60",
            "min_interval_seconds": "5",
            "max_interval_seconds": "20"
        }
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Arquivo {config_path} atualizado!")
            print("📋 Configuração:")
            for key, value in config_data.items():
                print(f"   {key}: {value}")
            
            return True
        except Exception as e:
            print(f"❌ Erro ao atualizar config.json: {e}")
            return False
    
    def mostrar_instrucoes_instalacao(self):
        """Mostra instruções de instalação de dependências"""
        print("🔧 INSTALAÇÃO DE DEPENDÊNCIAS NECESSÁRIAS")
        print("=" * 50)
        
        if not self.verificar_node():
            print("\n📥 INSTALAR NODE.JS:")
            print("   macOS: brew install node")
            print("   Ubuntu: sudo apt install nodejs npm")
            print("   Windows: Baixar de https://nodejs.org")
        
        if not self.verificar_git():
            print("\n📥 INSTALAR GIT:")
            print("   macOS: brew install git")
            print("   Ubuntu: sudo apt install git")
            print("   Windows: Baixar de https://git-scm.com")
        
        print("\n🔄 Depois de instalar, execute novamente:")
        print("   python setup_evolution_standalone.py --setup")


def main():
    setup = EvolutionAPISetup()
    
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        
        if comando == '--check':
            print("🔍 Verificando dependências...")
            setup.verificar_node()
            setup.verificar_npm()
            setup.verificar_git()
            
        elif comando == '--setup':
            print("🚀 CONFIGURAÇÃO COMPLETA DA EVOLUTION API")
            print("=" * 50)
            
            # Verificar dependências
            if not setup.verificar_node() or not setup.verificar_npm() or not setup.verificar_git():
                setup.mostrar_instrucoes_instalacao()
                return
            
            # Setup completo
            steps = [
                ("Clonar Evolution API", setup.clonar_evolution_api),
                ("Instalar dependências", setup.instalar_dependencias),
                ("Criar arquivo .env", setup.criar_env_file),
                ("Atualizar config.json", setup.atualizar_config_json)
            ]
            
            for step_name, step_func in steps:
                print(f"\n🔄 {step_name}...")
                if not step_func():
                    print(f"❌ Falha em: {step_name}")
                    return
            
            print("\n🎉 SETUP CONCLUÍDO!")
            print("📋 PRÓXIMOS PASSOS:")
            print("1. python setup_evolution_standalone.py --start")
            print("2. python setup_evolution_standalone.py --create-instance")
            print("3. python setup_evolution_standalone.py --connect")
            
        elif comando == '--start':
            setup.iniciar_evolution_api()
            
        elif comando == '--create-instance':
            setup.criar_instancia()
            
        elif comando == '--connect':
            setup.conectar_instancia()
            
        elif comando == '--status':
            setup.verificar_api_rodando()
            
        else:
            print("❌ Comando inválido!")
            print("Comandos disponíveis:")
            print("  --check          : Verificar dependências")
            print("  --setup          : Setup completo")
            print("  --start          : Iniciar Evolution API")
            print("  --create-instance: Criar instância WhatsApp")
            print("  --connect        : Conectar instância")
            print("  --status         : Verificar se API está rodando")
    
    else:
        print("🚀 EVOLUTION API SETUP - Versão Standalone")
        print("=" * 50)
        print("Este script configura Evolution API sem Docker")
        print("")
        print("📋 COMANDOS:")
        print("  python setup_evolution_standalone.py --check")
        print("  python setup_evolution_standalone.py --setup")
        print("  python setup_evolution_standalone.py --start")
        print("  python setup_evolution_standalone.py --create-instance")
        print("  python setup_evolution_standalone.py --connect")
        print("  python setup_evolution_standalone.py --status")
        print("")
        print("💡 Para começar, execute:")
        print("   python setup_evolution_standalone.py --check")


if __name__ == "__main__":
    main()