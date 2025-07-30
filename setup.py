#!/usr/bin/env python3
"""
Setup script para WhatsApp API Sender
Gera arquivos necessários e executa configuração inicial
"""

import os
import sys
from utils import create_sample_excel


def main():
    """Executa a configuração inicial do projeto"""
    
    print("🚀 WhatsApp API Sender - Configuração Inicial")
    print("=" * 50)
    
    # Criar arquivo Excel de exemplo
    print("\n📋 Criando arquivo Excel de exemplo...")
    try:
        create_sample_excel('sample.xlsx')
        print("✅ Arquivo sample.xlsx criado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar sample.xlsx: {e}")
    
    # Verificar se config.json existe
    if not os.path.exists('config.json'):
        print("\n⚠️  Arquivo config.json não encontrado!")
        print("📝 Configure suas credenciais da API no arquivo config.json")
    else:
        print("\n✅ Arquivo config.json encontrado")
    
    # Verificar dependências
    print("\n📦 Verificando dependências...")
    try:
        import requests
        import openpyxl
        print("✅ Dependências básicas instaladas")
    except ImportError as e:
        print(f"❌ Dependência ausente: {e}")
        print("💡 Execute: pip install -r requirements.txt")
    
    print("\n🎉 Configuração inicial concluída!")
    print("\n📋 Próximos passos:")
    print("1. Configure suas credenciais da API no config.json")
    print("2. Use sample.xlsx como modelo para sua planilha")
    print("3. Execute: python main.py")


if __name__ == "__main__":
    main() 