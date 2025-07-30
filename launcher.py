#!/usr/bin/env python3
"""
WhatsApp API Sender - Launcher
Permite escolher entre interface de linha de comando (CLI) ou interface gráfica (GUI)
"""

import sys
import argparse


def main():
    """Launcher principal que permite escolher CLI ou GUI"""
    
    parser = argparse.ArgumentParser(description='WhatsApp API Sender - Sistema de Envio em Massa')
    parser.add_argument('--web', action='store_true', 
                       help='Abrir interface web (recomendado)')
    parser.add_argument('--gui', action='store_true', 
                       help='Abrir interface gráfica (GUI)')
    parser.add_argument('--cli', action='store_true', 
                       help='Usar interface de linha de comando (CLI)')
    
    args = parser.parse_args()
    
    # Se nenhuma opção for especificada, mostrar menu
    if not args.web and not args.gui and not args.cli:
        print("🚀 WhatsApp API Sender")
        print("=" * 40)
        print("Escolha a interface:")
        print("1. 🌐 Interface Web (recomendado)")
        print("2. 🖥️  Interface Gráfica (GUI)")
        print("3. 💻 Linha de Comando (CLI)")
        print("4. ❌ Sair")
        
        try:
            choice = input("\nDigite sua escolha (1-4): ").strip()
            
            if choice == "1":
                args.web = True
            elif choice == "2":
                args.gui = True
            elif choice == "3":
                args.cli = True
            elif choice == "4":
                print("👋 Até logo!")
                return
            else:
                print("❌ Opção inválida!")
                return
        except KeyboardInterrupt:
            print("\n👋 Até logo!")
            return
    
    # Executar interface escolhida
    if args.web:
        try:
            print("🌐 Iniciando interface web...")
            from web_gui import main as web_main
            web_main()
        except ImportError as e:
            print("❌ Erro ao importar interface web:")
            print(f"   {str(e)}")
            print("\n💡 Instale as dependências web:")
            print("   pip install Flask Werkzeug")
        except Exception as e:
            print(f"❌ Erro na interface web: {str(e)}")
    
    elif args.gui:
        try:
            print("🖥️ Iniciando interface gráfica...")
            from gui import main as gui_main
            gui_main()
        except ImportError as e:
            print("❌ Erro ao importar interface gráfica:")
            print(f"   {str(e)}")
            print("\n💡 Instale as dependências GUI:")
            print("   pip install customtkinter Pillow")
        except Exception as e:
            print(f"❌ Erro na interface gráfica: {str(e)}")
    
    elif args.cli:
        try:
            print("💻 Iniciando interface de linha de comando...")
            from main import main as cli_main
            cli_main()
        except Exception as e:
            print(f"❌ Erro na interface CLI: {str(e)}")


if __name__ == "__main__":
    main() 