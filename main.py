#!/usr/bin/env python3
"""
WhatsApp API Sender - Main Module
Sistema de envio em massa de mensagens via WhatsApp usando APIs alternativas
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

from utils import (
    load_config,
    setup_logging,
    load_contacts_from_excel,
    validate_phone_number,
    wait_random_interval
)
from api_sender import WhatsAppAPISender


def main():
    """Função principal que coordena o envio de mensagens em massa"""
    
    # Configurar logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("🚀 WhatsApp API Sender - Envio em Massa de Mensagens")
    print("=" * 60)
    
    try:
        # Carregar configurações
        config = load_config()
        logger.info("Configurações carregadas com sucesso")
        
        # Solicitar caminho da planilha
        excel_path = input("\n📋 Digite o caminho da planilha Excel (.xlsx): ").strip()
        
        if not excel_path:
            print("❌ Caminho da planilha não pode estar vazio!")
            return
        
        if not os.path.exists(excel_path):
            print(f"❌ Arquivo não encontrado: {excel_path}")
            return
        
        # Carregar contatos da planilha
        print("\n📖 Carregando contatos da planilha...")
        contacts = load_contacts_from_excel(excel_path)
        
        if not contacts:
            print("❌ Nenhum contato válido encontrado na planilha!")
            return
        
        print(f"✅ {len(contacts)} contatos carregados")
        
        # Validar números de telefone
        print("\n🔍 Validando números de telefone...")
        valid_contacts = []
        invalid_count = 0
        
        for contact in contacts:
            if validate_phone_number(contact['numero']):
                valid_contacts.append(contact)
            else:
                invalid_count += 1
                logger.warning(f"Número inválido: {contact['numero']}")
        
        if invalid_count > 0:
            print(f"⚠️  {invalid_count} números inválidos foram ignorados")
        
        print(f"✅ {len(valid_contacts)} números válidos para envio")
        
        if not valid_contacts:
            print("❌ Nenhum número válido para envio!")
            return
        
        # Confirmar envio
        print(f"\n📱 Você está prestes a enviar {len(valid_contacts)} mensagens")
        confirm = input("Deseja continuar? (s/n): ").strip().lower()
        
        if confirm not in ['s', 'sim', 'y', 'yes']:
            print("❌ Envio cancelado pelo usuário")
            return
        
        # Inicializar sender
        sender = WhatsAppAPISender(config)
        
        # Estatísticas
        success_count = 0
        error_count = 0
        
        print(f"\n🚀 Iniciando envio de {len(valid_contacts)} mensagens...")
        print("=" * 60)
        
        # Enviar mensagens
        for i, contact in enumerate(valid_contacts, 1):
            numero = contact['numero']
            nome = contact.get('nome', 'Contato')
            mensagem = contact.get('mensagem', '')
            caminho_midia = contact.get('caminho_midia', '')
            
            print(f"\n[{i}/{len(valid_contacts)}] Enviando para {nome} ({numero})")
            
            try:
                # Verificar se arquivo de mídia existe (se especificado)
                if caminho_midia and not os.path.exists(caminho_midia):
                    logger.error(f"Arquivo de mídia não encontrado: {caminho_midia}")
                    sender.log_result(numero, 'erro', 'Arquivo de mídia não encontrado')
                    error_count += 1
                    continue
                
                # Enviar mensagem
                success = sender.send_message(
                    numero=numero,
                    mensagem=mensagem,
                    caminho_midia=caminho_midia
                )
                
                if success:
                    print(f"✅ Mensagem enviada com sucesso!")
                    success_count += 1
                else:
                    print(f"❌ Falha no envio da mensagem")
                    error_count += 1
                
            except Exception as e:
                logger.error(f"Erro no envio para {numero}: {str(e)}")
                sender.log_result(numero, 'erro', str(e))
                print(f"❌ Erro: {str(e)}")
                error_count += 1
            
            # Aguardar intervalo aleatório (exceto na última mensagem)
            if i < len(valid_contacts):
                wait_time = wait_random_interval()
                print(f"⏳ Aguardando {wait_time} segundos...")
        
        # Resumo final
        print("\n" + "=" * 60)
        print("📊 RESUMO FINAL")
        print("=" * 60)
        print(f"✅ Mensagens enviadas com sucesso: {success_count}")
        print(f"❌ Mensagens com erro: {error_count}")
        print(f"📋 Total processado: {len(valid_contacts)}")
        
        if success_count > 0:
            success_rate = (success_count / len(valid_contacts)) * 100
            print(f"📈 Taxa de sucesso: {success_rate:.1f}%")
        
        log_file = sender.get_log_filename()
        print(f"📄 Log salvo em: {log_file}")
        
        logger.info(f"Envio concluído: {success_count} sucessos, {error_count} erros")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Envio interrompido pelo usuário")
        logger.info("Envio interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro fatal: {str(e)}")
        logger.error(f"Erro fatal: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 