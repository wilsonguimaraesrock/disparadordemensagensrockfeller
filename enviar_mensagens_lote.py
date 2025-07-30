#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Disparador de Mensagens em Lote WhatsApp
Sistema principal para envio em massa via Evolution API e WAHA
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
import json

# Importar módulos locais
from utils import (
    load_config,
    setup_logging,
    load_contacts_from_excel,
    validate_phone_number,
    wait_random_interval
)
from api_sender import WhatsAppAPISender


def print_banner():
    """Exibe banner do sistema"""
    print("🚀" + "=" * 58 + "🚀")
    print("🎯  DISPARADOR DE MENSAGENS EM LOTE WHATSAPP  🎯")
    print("🚀" + "=" * 58 + "🚀")
    print("📱 Suporte: Evolution API + WAHA")
    print("🎥 Mídia: Imagens, Vídeos, Áudios, Documentos")
    print("⚡ Envio inteligente com retry automático")
    print("-" * 60)


def verificar_sistema():
    """Verifica se o sistema está pronto para uso"""
    print("🔍 Verificando sistema...")
    
    # Verificar arquivos essenciais
    arquivos_essenciais = ['config.json', 'utils.py', 'api_sender.py']
    for arquivo in arquivos_essenciais:
        if not os.path.exists(arquivo):
            print(f"❌ Arquivo essencial não encontrado: {arquivo}")
            return False
    
    # Verificar configuração
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if not config.get('provider') or not config.get('base_url'):
            print("❌ Configuração inválida em config.json")
            return False
            
        print(f"✅ Provider configurado: {config.get('provider', 'N/A')}")
        print(f"✅ URL base: {config.get('base_url', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Erro ao verificar configuração: {e}")
        return False
    
    print("✅ Sistema verificado com sucesso!")
    return True


def solicitar_arquivo_excel():
    """Solicita e valida arquivo Excel"""
    while True:
        print("\n📋 ARQUIVO DE CONTATOS")
        print("Formatos aceitos: .xlsx, .xls")
        print("Colunas necessárias: numero, mensagem, nome (opcional), caminho_midia (opcional)")
        
        excel_path = input("\n📂 Digite o caminho do arquivo Excel: ").strip()
        
        if not excel_path:
            print("❌ Caminho não pode estar vazio!")
            continue
        
        # Remover aspas se presentes
        excel_path = excel_path.strip('"\'')
        
        if not os.path.exists(excel_path):
            print(f"❌ Arquivo não encontrado: {excel_path}")
            opcao = input("Tentar novamente? (s/n): ").strip().lower()
            if opcao not in ['s', 'sim']:
                return None
            continue
        
        if not excel_path.lower().endswith(('.xlsx', '.xls')):
            print("❌ Arquivo deve ser Excel (.xlsx ou .xls)")
            continue
        
        return excel_path


def processar_contatos(excel_path):
    """Processa e valida contatos do Excel"""
    print(f"\n📖 Carregando contatos de: {os.path.basename(excel_path)}")
    
    try:
        contacts = load_contacts_from_excel(excel_path)
        
        if not contacts:
            print("❌ Nenhum contato encontrado na planilha!")
            return None
        
        print(f"📋 {len(contacts)} contatos carregados")
        
        # Validar números
        print("🔍 Validando números de telefone...")
        valid_contacts = []
        invalid_count = 0
        
        for contact in contacts:
            numero = contact.get('numero', '')
            if validate_phone_number(numero):
                valid_contacts.append(contact)
            else:
                invalid_count += 1
                print(f"⚠️  Número inválido ignorado: {numero}")
        
        if invalid_count > 0:
            print(f"⚠️  {invalid_count} números inválidos foram ignorados")
        
        print(f"✅ {len(valid_contacts)} números válidos para envio")
        
        if not valid_contacts:
            print("❌ Nenhum número válido encontrado!")
            return None
            
        return valid_contacts
        
    except Exception as e:
        print(f"❌ Erro ao processar arquivo: {e}")
        return None


def confirmar_envio(contacts):
    """Confirma o envio com o usuário"""
    print(f"\n📊 RESUMO DO ENVIO")
    print("-" * 40)
    print(f"📱 Total de contatos: {len(contacts)}")
    
    # Contar tipos de mídia
    com_midia = sum(1 for c in contacts if c.get('caminho_midia'))
    sem_midia = len(contacts) - com_midia
    
    print(f"💬 Mensagens de texto: {sem_midia}")
    print(f"🎥 Mensagens com mídia: {com_midia}")
    
    # Mostrar exemplos
    if contacts:
        print(f"\n📋 Exemplos:")
        for i, contact in enumerate(contacts[:3], 1):
            numero = contact.get('numero', 'N/A')
            nome = contact.get('nome', 'Sem nome')
            tem_midia = "📎" if contact.get('caminho_midia') else "💬"
            print(f"  {i}. {tem_midia} {nome} ({numero})")
        
        if len(contacts) > 3:
            print(f"  ... e mais {len(contacts) - 3} contatos")
    
    print("-" * 40)
    print("⚠️  ATENÇÃO: Esta operação irá enviar mensagens via WhatsApp!")
    
    while True:
        confirm = input(f"\n🚀 Enviar {len(contacts)} mensagens? (s/n): ").strip().lower()
        if confirm in ['s', 'sim', 'y', 'yes']:
            return True
        elif confirm in ['n', 'não', 'nao', 'no']:
            return False
        else:
            print("❌ Digite 's' para SIM ou 'n' para NÃO")


def executar_envios(contacts, config):
    """Executa o envio das mensagens"""
    print(f"\n🚀 INICIANDO ENVIO DE {len(contacts)} MENSAGENS")
    print("=" * 60)
    
    # Inicializar sender
    sender = WhatsAppAPISender(config)
    
    # Estatísticas
    stats = {
        'total': len(contacts),
        'sucesso': 0,
        'erro': 0,
        'inicio': datetime.now()
    }
    
    # Enviar mensagens
    for i, contact in enumerate(contacts, 1):
        numero = contact.get('numero', '')
        nome = contact.get('nome', 'Contato')
        mensagem = contact.get('mensagem', '')
        caminho_midia = contact.get('caminho_midia', '')
        
        print(f"\n[{i}/{stats['total']}] 📱 {nome} ({numero})")
        print(f"💬 Mensagem: {mensagem[:50]}{'...' if len(mensagem) > 50 else ''}")
        
        if caminho_midia:
            print(f"📎 Mídia: {os.path.basename(caminho_midia)}")
            
            # Verificar se arquivo de mídia existe
            if not os.path.exists(caminho_midia):
                print(f"❌ Arquivo não encontrado: {caminho_midia}")
                sender.log_result(numero, 'erro', 'Arquivo de mídia não encontrado')
                stats['erro'] += 1
                continue
        
        try:
            # Enviar mensagem
            success = sender.send_message(
                numero=numero,
                mensagem=mensagem,
                caminho_midia=caminho_midia
            )
            
            if success:
                print(f"✅ Enviado com sucesso!")
                stats['sucesso'] += 1
            else:
                print(f"❌ Falha no envio")
                stats['erro'] += 1
                
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            sender.log_result(numero, 'erro', str(e))
            stats['erro'] += 1
        
        # Progresso
        percentual = (i / stats['total']) * 100
        print(f"📊 Progresso: {percentual:.1f}% | ✅ {stats['sucesso']} | ❌ {stats['erro']}")
        
        # Aguardar intervalo (exceto na última mensagem)
        if i < stats['total']:
            wait_time = wait_random_interval()
            print(f"⏳ Aguardando {wait_time}s...")
    
    # Mostrar resumo final
    mostrar_resumo_final(stats, sender.log_filename)


def mostrar_resumo_final(stats, log_filename):
    """Mostra resumo final dos envios"""
    stats['fim'] = datetime.now()
    duracao = stats['fim'] - stats['inicio']
    
    print("\n" + "=" * 60)
    print("📊 RESUMO FINAL")
    print("=" * 60)
    print(f"📱 Total processado: {stats['total']}")
    print(f"✅ Enviados com sucesso: {stats['sucesso']}")
    print(f"❌ Falhas: {stats['erro']}")
    
    if stats['total'] > 0:
        taxa_sucesso = (stats['sucesso'] / stats['total']) * 100
        print(f"📈 Taxa de sucesso: {taxa_sucesso:.1f}%")
    
    print(f"⏱️  Tempo total: {duracao}")
    print(f"📄 Log salvo em: {log_filename}")
    
    # Análise de performance
    if taxa_sucesso >= 90:
        print("🎉 Excelente! Taxa de sucesso muito alta!")
    elif taxa_sucesso >= 75:
        print("👍 Boa taxa de sucesso!")
    elif taxa_sucesso >= 50:
        print("⚠️  Taxa de sucesso moderada. Verifique os logs.")
    else:
        print("🚨 Taxa de sucesso baixa! Verifique configuração e conectividade.")
    
    print("=" * 60)


def main():
    """Função principal"""
    print_banner()
    
    # Configurar logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Verificar sistema
        if not verificar_sistema():
            print("\n❌ Sistema não está pronto. Corrija os problemas e tente novamente.")
            return
        
        # Carregar configurações
        config = load_config()
        logger.info("Sistema iniciado com sucesso")
        
        # Solicitar arquivo Excel
        excel_path = solicitar_arquivo_excel()
        if not excel_path:
            print("❌ Operação cancelada pelo usuário.")
            return
        
        # Processar contatos
        contacts = processar_contatos(excel_path)
        if not contacts:
            print("❌ Não foi possível processar os contatos.")
            return
        
        # Confirmar envio
        if not confirmar_envio(contacts):
            print("❌ Envio cancelado pelo usuário.")
            return
        
        # Executar envios
        executar_envios(contacts, config)
        
        print("\n🎉 Processo concluído! Verifique os logs para detalhes.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação interrompida pelo usuário.")
        logger.info("Operação interrompida pelo usuário")
        
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        logger.error(f"Erro inesperado: {e}")


if __name__ == "__main__":
    main()
