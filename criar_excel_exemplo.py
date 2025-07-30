#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Criador de Arquivo Excel de Exemplo
Gera planilha de exemplo para teste do sistema
"""

import pandas as pd
import os
from datetime import datetime


def criar_excel_exemplo():
    """Cria arquivo Excel de exemplo para testes"""
    
    # Dados de exemplo
    dados = [
        {
            'numero': '+5521999887766',
            'nome': 'João Silva',
            'mensagem': 'Olá! Esta é uma mensagem de teste do nosso sistema automatizado. 🚀',
            'caminho_midia': ''  # Mensagem somente texto
        },
        {
            'numero': '+5511988776655',
            'nome': 'Maria Santos',
            'mensagem': 'Teste com imagem anexa',
            'caminho_midia': 'arquivos_teste/teste.svg'  # Mensagem com imagem
        },
        {
            'numero': '+5531977665544',
            'nome': 'Pedro Costa',
            'mensagem': 'Documento de teste para verificação',
            'caminho_midia': 'arquivos_teste/teste.txt'  # Mensagem com documento
        },
        {
            'numero': '5541966554433',  # Sem + no início (será validado)
            'nome': 'Ana Oliveira',
            'mensagem': 'Mensagem de teste sem mídia para Ana Oliveira.',
            'caminho_midia': ''
        },
        {
            'numero': '+5551955443322',
            'nome': 'Carlos Mendes',
            'mensagem': 'Teste final do sistema 📱✅',
            'caminho_midia': ''
        }
    ]
    
    # Criar DataFrame
    df = pd.DataFrame(dados)
    
    # Nome do arquivo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'exemplo_contatos_{timestamp}.xlsx'
    
    try:
        # Salvar Excel
        df.to_excel(filename, index=False, sheet_name='Contatos')
        
        print("✅ Arquivo Excel de exemplo criado!")
        print(f"📄 Arquivo: {filename}")
        print(f"📊 {len(dados)} contatos de exemplo")
        print("")
        print("📋 ESTRUTURA DA PLANILHA:")
        print("   • numero: Número do WhatsApp (com ou sem +)")
        print("   • nome: Nome do contato (opcional)")
        print("   • mensagem: Texto da mensagem")
        print("   • caminho_midia: Caminho do arquivo (opcional)")
        print("")
        print("💡 Para usar este arquivo:")
        print(f"   python enviar_mensagens_lote.py")
        print(f"   Digite: {filename}")
        
        return filename
        
    except ImportError:
        print("❌ Pandas não instalado!")
        print("📦 Para instalar: pip install pandas openpyxl")
        return None
    except Exception as e:
        print(f"❌ Erro ao criar Excel: {e}")
        return None


def criar_excel_simples():
    """Cria Excel simples sem usar pandas"""
    import csv
    
    dados = [
        ['numero', 'nome', 'mensagem', 'caminho_midia'],
        ['+5521999887766', 'João Silva', 'Olá! Mensagem de teste 🚀', ''],
        ['+5511988776655', 'Maria Santos', 'Teste com imagem', 'arquivos_teste/teste.svg'],
        ['+5531977665544', 'Pedro Costa', 'Documento de teste', 'arquivos_teste/teste.txt'],
        ['5541966554433', 'Ana Oliveira', 'Mensagem sem mídia', ''],
        ['+5551955443322', 'Carlos Mendes', 'Teste final 📱✅', '']
    ]
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'exemplo_contatos_{timestamp}.csv'
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(dados)
        
        print("✅ Arquivo CSV de exemplo criado!")
        print(f"📄 Arquivo: {filename}")
        print(f"📊 {len(dados)-1} contatos de exemplo")
        print("")
        print("⚠️  NOTA: O sistema funciona melhor com arquivos .xlsx")
        print("💡 Para converter CSV para Excel, use uma planilha eletrônica")
        
        return filename
        
    except Exception as e:
        print(f"❌ Erro ao criar CSV: {e}")
        return None


def verificar_arquivos_teste():
    """Verifica se existem arquivos de teste na pasta arquivos_teste"""
    pasta_teste = 'arquivos_teste'
    
    if not os.path.exists(pasta_teste):
        print(f"📁 Criando pasta: {pasta_teste}")
        os.makedirs(pasta_teste)
    
    # Verificar arquivos de teste
    arquivos_necessarios = {
        'teste.txt': 'Arquivo de texto de teste',
        'teste.svg': 'Imagem SVG de teste',
        'teste.json': 'Arquivo JSON de teste'
    }
    
    for arquivo, descricao in arquivos_necessarios.items():
        caminho = os.path.join(pasta_teste, arquivo)
        if os.path.exists(caminho):
            tamanho = os.path.getsize(caminho)
            print(f"✅ {arquivo}: {tamanho} bytes")
        else:
            print(f"⚠️  {arquivo}: não encontrado")
    
    return pasta_teste


def main():
    print("📄 CRIADOR DE ARQUIVO EXCEL DE EXEMPLO")
    print("=" * 50)
    
    # Verificar arquivos de teste
    verificar_arquivos_teste()
    print("")
    
    # Tentar criar Excel com pandas
    print("🔄 Tentando criar arquivo Excel...")
    filename = criar_excel_exemplo()
    
    if not filename:
        print("\n🔄 Criando arquivo CSV alternativo...")
        filename = criar_excel_simples()
    
    if filename:
        print(f"\n🎉 Arquivo criado: {filename}")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. python enviar_mensagens_lote.py")
        print(f"2. Digite o nome do arquivo: {filename}")
        print("3. Confirme o envio")
    else:
        print("\n❌ Não foi possível criar arquivo de exemplo")


if __name__ == "__main__":
    main()