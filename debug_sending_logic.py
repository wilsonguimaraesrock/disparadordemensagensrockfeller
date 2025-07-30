#!/usr/bin/env python3
"""
Script para debugar a lógica de envio de mensagens
"""

import json
import time
from datetime import datetime

def debug_sending_logic():
    """Simular a lógica de envio para identificar o problema"""
    
    # Simular dados de teste
    contacts_to_send = [
        {'numero': '+5547996322763', 'nome': 'Contato 1'},
        {'numero': '+5547996322764', 'nome': 'Contato 2'},
        {'numero': '+5547996322765', 'nome': 'Contato 3'}
    ]
    
    sequence = [
        {'type': 'text', 'content': 'Primeira mensagem para {nome}'},
        {'type': 'text', 'content': 'Segunda mensagem para {nome}'},
        {'type': 'text', 'content': 'Terceira mensagem para {nome}'}
    ]
    
    print(f"🚀 Iniciando simulação para {len(contacts_to_send)} contatos")
    print(f"📝 Sequência de {len(sequence)} mensagens")
    print("=" * 60)
    
    message_count = 0
    
    # Loop principal - CONTATOS
    for contact_idx, contact in enumerate(contacts_to_send):
        numero = contact['numero']
        nome = contact['nome']
        
        print(f"\n👤 CONTATO {contact_idx + 1}: {nome} ({numero})")
        print(f"📋 Enviando sequência de {len(sequence)} mensagens...")
        
        # Loop interno - MENSAGENS DA SEQUÊNCIA
        for msg_idx, message in enumerate(sequence):
            message_count += 1
            
            texto = message['content'].replace('{nome}', nome)
            print(f"  📤 Mensagem {msg_idx + 1}/{len(sequence)}: {texto}")
            
            # Simular envio
            time.sleep(0.1)  # Simular tempo de envio
            print(f"  ✅ Mensagem {msg_idx + 1} enviada para {nome}")
            
            # INTERVALO ENTRE MENSAGENS DA SEQUÊNCIA
            if msg_idx < len(sequence) - 1:  # Não na última mensagem da sequência
                wait_time = 2  # Simular 2 segundos
                print(f"  ⏳ Aguardando {wait_time}s antes da próxima mensagem...")
                time.sleep(wait_time)
        
        # INTERVALO ENTRE CONTATOS
        if contact_idx < len(contacts_to_send) - 1:  # Não no último contato
            wait_time = 5  # Simular 5 segundos
            print(f"\n⏳ Aguardando {wait_time}s antes do próximo contato...")
            time.sleep(wait_time)
    
    print("\n" + "=" * 60)
    print(f"🎉 SIMULAÇÃO CONCLUÍDA!")
    print(f"📊 Total de mensagens enviadas: {message_count}")
    print(f"📊 Esperado: {len(contacts_to_send) * len(sequence)}")
    
    # Verificar se a lógica está correta
    expected = len(contacts_to_send) * len(sequence)
    if message_count == expected:
        print("✅ Lógica está CORRETA")
    else:
        print("❌ Lógica tem PROBLEMA")

if __name__ == "__main__":
    debug_sending_logic()