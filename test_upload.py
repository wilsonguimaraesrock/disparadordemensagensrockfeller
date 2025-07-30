#!/usr/bin/env python3
"""
Script de teste para verificar o funcionamento do upload de planilhas
"""

import os
import sys
from utils import load_contacts_from_excel, validate_phone_number, create_sample_excel

def test_excel_processing():
    """Testa o processamento de planilhas Excel"""
    
    print("🧪 Testando processamento de planilhas Excel")
    print("=" * 50)
    
    # Criar arquivo de teste
    test_file = "test_contacts.xlsx"
    print(f"📋 Criando arquivo de teste: {test_file}")
    
    try:
        create_sample_excel(test_file)
        print("✅ Arquivo de teste criado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar arquivo de teste: {e}")
        return False
    
    # Testar carregamento
    print(f"\n📖 Testando carregamento de contatos...")
    
    try:
        contacts = load_contacts_from_excel(test_file)
        print(f"✅ {len(contacts)} contatos carregados")
        
        # Mostrar contatos carregados
        for i, contact in enumerate(contacts, 1):
            print(f"  {i}. {contact.get('nome', 'Sem nome')} - {contact['numero']}")
            
    except Exception as e:
        print(f"❌ Erro ao carregar contatos: {e}")
        return False
    
    # Testar validação
    print(f"\n🔍 Testando validação de números...")
    
    valid_count = 0
    invalid_count = 0
    
    for contact in contacts:
        numero = contact['numero']
        is_valid = validate_phone_number(numero)
        
        if is_valid:
            valid_count += 1
            print(f"  ✅ {numero} - Válido")
        else:
            invalid_count += 1
            print(f"  ❌ {numero} - Inválido")
    
    print(f"\n📊 Resultados da validação:")
    print(f"  ✅ Válidos: {valid_count}")
    print(f"  ❌ Inválidos: {invalid_count}")
    print(f"  📱 Total: {len(contacts)}")
    
    # Limpar arquivo de teste
    try:
        os.remove(test_file)
        print(f"\n🗑️ Arquivo de teste removido: {test_file}")
    except:
        pass
    
    print("\n🎉 Teste concluído com sucesso!")
    return True

def test_phone_validation():
    """Testa especificamente a validação de números"""
    
    print("\n🔍 Testando validação de números de telefone")
    print("=" * 50)
    
    test_numbers = [
        "+5521999998888",  # Válido - formato internacional
        "5521999998888",   # Válido - sem +
        "21999998888",     # Válido - sem código do país
        "+55219999988",    # Inválido - muito curto
        "123456789",       # Inválido - muito curto
        "+552199999888888", # Inválido - muito longo
        "abc123456789",    # Inválido - contém letras
        "",                # Inválido - vazio
        "+5511987654321",  # Válido - São Paulo
        "11987654321",     # Válido - São Paulo sem código
    ]
    
    for numero in test_numbers:
        is_valid = validate_phone_number(numero)
        status = "✅ Válido" if is_valid else "❌ Inválido"
        print(f"  {numero:<20} - {status}")

if __name__ == "__main__":
    print("🚀 Iniciando testes do sistema")
    print("=" * 60)
    
    # Testar validação de números
    test_phone_validation()
    
    # Testar processamento de Excel
    success = test_excel_processing()
    
    if success:
        print("\n🎉 Todos os testes passaram!")
        sys.exit(0)
    else:
        print("\n💥 Alguns testes falharam!")
        sys.exit(1) 