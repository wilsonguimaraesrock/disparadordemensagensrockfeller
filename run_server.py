#!/usr/bin/env python3
"""
WhatsApp API Sender - Web Server Launcher
Script para executar o servidor web em terminal separado
"""

import os
import sys
import webbrowser
import threading
import time
from pathlib import Path

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    
    missing_deps = []
    
    try:
        import flask
        print("✅ Flask instalado")
    except ImportError:
        missing_deps.append("Flask")
    
    try:
        import openpyxl
        print("✅ openpyxl instalado")
    except ImportError:
        missing_deps.append("openpyxl")
    
    try:
        import requests
        print("✅ requests instalado")
    except ImportError:
        missing_deps.append("requests")
    
    if missing_deps:
        print(f"\n❌ Dependências ausentes: {', '.join(missing_deps)}")
        print("💡 Execute: pip install -r requirements.txt")
        return False
    
    print("✅ Todas as dependências estão instaladas!")
    return True

def check_files():
    """Verifica se todos os arquivos necessários existem"""
    print("\n📁 Verificando arquivos do projeto...")
    
    required_files = [
        'web_gui.py',
        'utils.py',
        'api_sender.py',
        'config.json',
        'templates/base.html',
        'templates/index.html',
        'templates/config.html',
        'templates/message_config.html',
        'templates/contacts.html',
        'templates/send.html',
        'templates/logs.html'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Arquivos ausentes: {', '.join(missing_files)}")
        return False
    
    print("✅ Todos os arquivos estão presentes!")
    return True

def open_browser_delayed():
    """Abre o navegador após um delay"""
    time.sleep(2)
    print("🌐 Abrindo navegador...")
    webbrowser.open('http://127.0.0.1:5000')

def main():
    """Função principal"""
    
    print("🚀 WhatsApp API Sender - Web Server")
    print("=" * 50)
    
    # Verificar dependências
    if not check_dependencies():
        print("\n💥 Falha na verificação de dependências!")
        input("Pressione Enter para sair...")
        sys.exit(1)
    
    # Verificar arquivos
    if not check_files():
        print("\n💥 Falha na verificação de arquivos!")
        input("Pressione Enter para sair...")
        sys.exit(1)
    
    print("\n🎉 Verificações concluídas com sucesso!")
    print("\n" + "=" * 50)
    print("🌐 INICIANDO SERVIDOR WEB")
    print("=" * 50)
    print("📱 URL: http://127.0.0.1:5000")
    print("🛑 Para parar: Pressione Ctrl+C")
    print("=" * 50)
    
    # Agendar abertura do navegador
    browser_thread = threading.Thread(target=open_browser_delayed)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        # Importar e executar o servidor web
        from web_gui import app, load_initial_config
        
        # Carregar configuração inicial
        load_initial_config()
        
        # Executar servidor
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=False,
            use_reloader=False  # Evitar restart duplo
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor parado pelo usuário")
    except ImportError as e:
        print(f"\n❌ Erro ao importar módulo: {e}")
        print("🔍 Verifique se todos os arquivos estão no diretório correto")
    except Exception as e:
        print(f"\n💥 Erro fatal: {e}")
    finally:
        print("\n👋 Até logo!")

if __name__ == "__main__":
    main() 