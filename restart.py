#!/usr/bin/env python3
"""
Script para reiniciar o servidor WhatsApp API Sender
"""

import sys
import os
import webbrowser
import threading
import time

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def open_browser_delayed():
    """Abre o navegador após um delay"""
    time.sleep(3)
    print("🌐 Abrindo navegador...")
    webbrowser.open('http://127.0.0.1:5000')

def main():
    try:
        print("🚀 WhatsApp API Sender - Reiniciando")
        print("=" * 50)
        print("🔍 Carregando módulos...")
        
        from web_gui import app, load_initial_config
        
        print("⚙️ Carregando configuração inicial...")
        load_initial_config()
        
        print("🌐 Iniciando servidor na porta 5000...")
        print("📱 URL: http://127.0.0.1:5000")
        print("🛑 Para parar: Pressione Ctrl+C")
        print("=" * 50)
        
        # Agendar abertura do navegador
        browser_thread = threading.Thread(target=open_browser_delayed)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Executar servidor
        app.run(host='127.0.0.1', port=5000, debug=False)
        
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 