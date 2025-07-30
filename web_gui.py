#!/usr/bin/env python3
"""
WhatsApp API Sender - Web GUI
Interface web moderna para envio em massa de mensagens com suporte a sequências
"""

import os
import json
import threading
import logging
import random
import time
from datetime import datetime
from pathlib import Path
import webbrowser

from quart import Quart, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename

# Configuração de logging no início do arquivo
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from utils import (
    load_config,
    setup_logging,
    load_contacts_from_excel,
    validate_phone_number,
    create_sample_excel
)
from api_sender import WhatsAppAPISender
from whatsapp_web import whatsapp_manager
import base64
import asyncio
import aiohttp


app = Quart(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Criar pasta de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Criar pasta para templates se não existir
TEMPLATES_FOLDER = 'templates_saved'
os.makedirs(TEMPLATES_FOLDER, exist_ok=True)

# Variáveis globais para estado da aplicação
app_state = {
    'config': None,
    'contacts': [],
    'valid_contacts': [],
    'invalid_contacts': [],
    'sender': None,
    'sending_active': False,
    'send_progress': {
        'current': 0,
        'total': 0,
        'success': 0,
        'error': 0,
        'current_contact': '',
        'current_message': 1,
        'sequence_length': 1
    },
    'logs': [],
    'message_config': {
        'sequence': [],
        'interval': 10,  # Intervalo entre mensagens na sequência (segundos)
        'fallback_name': 'amigo(a)'
    }
}


@app.route('/@vite/client')
def vite_client():
    """Intercepta requisições do Vite client para evitar erros 404"""
    return '', 204  # No Content


@app.route('/vite-blocker.js')
async def vite_blocker_js():
    """Serve o service worker para bloquear requisições do Vite"""
    return await send_file('templates/vite-blocker.js', mimetype='application/javascript')


@app.route('/')
async def index():
    """Página principal"""
    return await render_template('index.html')


@app.route('/config')
async def config():
    """Página de configuração da API"""
    return await render_template('config.html')


@app.route('/message_config')
async def message_config():
    """Página de configuração de mensagens"""
    return await render_template('message_config.html')


@app.route('/contacts')
async def contacts():
    """Página de gerenciamento de contatos"""
    return await render_template('contacts.html')


@app.route('/send')
async def send():
    """Página de envio"""
    return await render_template('send.html')


@app.route('/logs')
async def logs():
    """Página de logs"""
    return await render_template('logs.html')


@app.route('/qr_waha')
async def qr_waha():
    """Página dedicada para QR code do WAHA"""
    return await render_template('qr_waha.html')

@app.route('/debug_status')
async def debug_status():
    """Página de debug para status WAHA"""
    return await send_from_directory('.', 'debug_status.html')


# API Endpoints

@app.route('/api/whatsapp/status')
async def whatsapp_status():
    """Verifica e retorna o status da conexão com o WhatsApp Web."""
    try:
        # Chama o método que verifica o estado da conexão
        status = await whatsapp_manager.check_connection_status_periodically()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error checking WhatsApp status: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/status')
def api_status():
    """Retorna status atual do sistema"""
    try:
        sequence = app_state['message_config'].get('sequence', [])
        
        status = {
            'config_ok': app_state['config'] is not None,
            'contacts_loaded': len(app_state['contacts']),
            'contacts_valid': len(app_state['valid_contacts']),
            'message_configured': len(sequence) > 0,
            'sending_active': app_state['sending_active'],
            'send_progress': app_state['send_progress'],
            'sequence_length': len(sequence)
        }
        
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/contacts_preview')
def api_contacts_preview():
    """Retorna preview dos contatos com informações de sequência e status."""
    # Inicializar stats para garantir que exista mesmo em caso de erro
    stats = {
        'loaded': len(app_state.get('contacts', [])),
        'valid': len(app_state.get('valid_contacts', [])),
        'invalid': len(app_state.get('invalid_contacts', []))
    }

    try:
        # Se a validação já ocorreu, usar a lista de válidos, senão, a lista completa
        if app_state['valid_contacts'] or app_state['invalid_contacts']:
            contacts_to_show = sorted(app_state['valid_contacts'], key=lambda c: c.get('id', 0))
        else:
            contacts_to_show = app_state.get('contacts', [])
            stats['valid'] = 0
            stats['invalid'] = 0
        
        # Obter sequência de mensagens
        sequence = app_state.get('message_config', {}).get('sequence', [])
        fallback_name = app_state.get('message_config', {}).get('fallback_name', 'amigo(a)')
        
        if sequence:
            first_message = sequence[0]
            if first_message.get('type') == 'text':
                preview_content = first_message.get('content', '')[:50] + "..." if len(first_message.get('content', '')) > 50 else first_message.get('content', '')
            else:
                media_type = first_message.get('mediaType', 'Mídia')
                file_path = first_message.get('path', '')
                preview_content = f"📎 {media_type.title()}: {os.path.basename(file_path) if file_path else 'arquivo'}"
            caminho_midia = f"Sequência: {len(sequence)} mensagens"
        else:
            preview_content = "Nenhuma sequência configurada"
            caminho_midia = ""
        
        preview_contacts = []
        limit = None if (app_state['valid_contacts'] or app_state['invalid_contacts']) else 20
        
        for contact in contacts_to_show[:limit]:
            nome = contact.get('nome', fallback_name)
            numero = contact.get('numero', '')
            status = contact.get('status', 'Não Validado')
            status_class = contact.get('status_class', 'warning')
            preview_message = preview_content.replace('{{nome}}', nome).replace('{nome}', nome)
            preview_contacts.append({
                'id': contact.get('id'),
                'nome': nome,
                'numero': numero,
                'mensagem': preview_message,
                'caminho_midia': caminho_midia,
                'status': status,
                'status_class': status_class
            })
        
        return jsonify({
            'success': True,
            'contacts': preview_contacts,
            'total': len(contacts_to_show),
            'stats': stats
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'contacts': [],
            'total': 0,
            'stats': stats,
            'error': str(e)
        })


@app.route('/api/save_message', methods=['POST'])
async def api_save_message():
    """Salvar configuração de sequência de mensagens"""
    try:
        data = await request.json
        
        # Validar sequência
        sequence = data.get('sequence', [])
        if not sequence:
            return jsonify({'success': False, 'error': 'Sequência não pode estar vazia'})
        
        # Validar cada mensagem da sequência
        for i, message in enumerate(sequence):
            if message.get('type') == 'text':
                if not message.get('content', '').strip():
                    return jsonify({'success': False, 'error': f'Mensagem {i+1}: Texto não pode estar vazio'})
            elif message.get('type') == 'media':
                if not message.get('path', '').strip():
                    return jsonify({'success': False, 'error': f'Mensagem {i+1}: Caminho da mídia não pode estar vazio'})
                if not message.get('mediaType'):
                    return jsonify({'success': False, 'error': f'Mensagem {i+1}: Tipo de mídia deve ser especificado'})
        
        app_state['message_config'] = {
            'sequence': sequence,
            'interval': max(1, min(300, data.get('interval', 10))),  # Entre 1 e 300 segundos
            'fallback_name': data.get('fallback_name', 'amigo(a)')
        }
        
        add_log(f"💬 Sequência de {len(sequence)} mensagens salva")
        
        return jsonify({'success': True, 'message': f'Sequência de {len(sequence)} mensagens salva com sucesso!'})
        
    except Exception as e:
        error_msg = f"Erro ao salvar sequência: {str(e)}"
        add_log(f"❌ {error_msg}")
        add_log("Erro durante o upload de contatos.", 'DEBUG')
        return jsonify({'success': False, 'error': error_msg})


@app.route('/api/get_message')
def api_get_message():
    """Obter configuração atual da sequência"""
    try:
        return jsonify({
            'success': True,
            'message': app_state['message_config']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/save_config', methods=['POST'])
async def api_save_config():
    """Salvar configuração da API"""
    try:
        config_data = await request.json
        
        # Validações básicas
        required_fields = ['provider', 'base_url']
        for field in required_fields:
            if not config_data.get(field):
                return jsonify({'success': False, 'error': f'Campo {field} é obrigatório'})
        
        # Salvar no config.json
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        # Atualizar estado
        app_state['config'] = config_data
        
        add_log(f"✅ Configuração salva: {config_data['provider']}")
        
        return jsonify({'success': True, 'message': 'Configuração salva com sucesso!'})
    except Exception as e:
        error_msg = f"Erro ao salvar configuração: {str(e)}"
        add_log(f"❌ {error_msg}")
        return jsonify({'success': False, 'error': error_msg})


@app.route('/api/get_config')
def api_get_config():
    """Obter configuração atual"""
    try:
        if app_state['config']:
            return jsonify({'success': True, 'config': app_state['config']})
        else:
            return jsonify({'success': False, 'error': 'Nenhuma configuração carregada'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/whatsapp/qr_code', methods=['POST'])
async def get_qr_code():
    """Gera e retorna o QR code para conexão com o WhatsApp Web."""
    try:
        # Garante que o navegador esteja rodando antes de prosseguir
        await whatsapp_manager.ensure_browser_is_running()

        qr_code_base64, error = await whatsapp_manager.get_qr_code()
        
        if error:
            return jsonify({'success': False, 'error': error}), 400
        
        if qr_code_base64:
            return jsonify({'success': True, 'qr_code': qr_code_base64})
        
        return jsonify({'success': False, 'error': 'Não foi possível obter o QR Code.'}), 400

    except Exception as e:
        logging.error(f"Erro ao gerar QR Code: {e}")
        # Tenta fechar a sessão para limpar o estado
        await whatsapp_manager.close_session()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/whatsapp/status')
async def get_whatsapp_status():
    """Verifica e retorna o status da conexão com o WhatsApp Web."""
    try:
        # This now calls the periodic check, which updates the status internally
        status = await whatsapp_manager.check_connection_status_periodically()
        return jsonify(status)
    except Exception as e:
        logging.error(f"Erro ao verificar status do WhatsApp: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/config', methods=['GET', 'POST'])
async def api_config():
    """Endpoint de compatibilidade para config"""
    if request.method == 'GET':
        return api_get_config()
    else:  # POST
        return await api_save_config()


@app.route('/api/upload_contacts', methods=['POST'])
async def api_upload_contacts():
    logging.debug("Iniciando o upload de contatos...")
    try:
        files = await request.files
        if 'file' not in files:
            return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'})
        
        file = files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nenhum arquivo selecionado'})
        
        if not file.filename.lower().endswith('.xlsx'):
            return jsonify({'success': False, 'error': 'Apenas arquivos .xlsx são aceitos'})
        
        # Usar caminho absoluto para garantir consistência
        upload_folder = Path(app.config['UPLOAD_FOLDER']).resolve()
        os.makedirs(upload_folder, exist_ok=True)

        filename = secure_filename(file.filename)
        filepath = upload_folder / filename
        
        # Salvar o arquivo (converter Path para string)
        await file.save(str(filepath))

        # Verificar se o arquivo foi salvo corretamente antes de prosseguir
        if not filepath.exists():
            error_msg = f"Falha ao salvar o arquivo em {filepath}. Verifique as permissões do diretório."
            add_log(f"❌ {error_msg}")
            return jsonify({'success': False, 'error': error_msg})

        try:
            # Limpar completamente o estado dos contatos antes de carregar novos
            app_state['contacts'] = []
            app_state['valid_contacts'] = []
            app_state['invalid_contacts'] = []

            # Processar contatos
            contacts = load_contacts_from_excel(str(filepath))

            app_state['contacts'] = contacts
            add_log(f"📋 {len(contacts)} contatos carregados da planilha: {filename}")
            logging.debug("Finalizado o upload de contatos.")

            return jsonify({
                'success': True,
                'message': f'{len(contacts)} contatos carregados com sucesso!',
                'contacts': contacts,
                'stats': {
                    'total': len(contacts),
                    'valid': 0,  # Validação ainda não foi feita
                    'invalid': 0
                }
            })
        except FileNotFoundError:
            error_msg = f"Erro ao processar planilha: Arquivo Excel não encontrado em {filepath}"
            add_log(f"❌ {error_msg}")
            return jsonify({'success': False, 'error': error_msg})
        except Exception as e:
            # Captura outras exceções, incluindo erros de openpyxl
            error_msg = f"Erro ao processar planilha: {str(e)}"
            add_log(f"❌ {error_msg}")
            return jsonify({'success': False, 'error': error_msg})
        finally:
            # Garantir que o arquivo temporário seja removido após o processamento
            if filepath.exists():
                os.remove(filepath)
        

        
    except Exception as e:
        error_msg = f"Erro ao processar planilha: {str(e)}"
        add_log(f"❌ {error_msg}")
        return jsonify({'success': False, 'error': error_msg})


@app.route('/api/update_contact/<int:contact_id>', methods=['POST'])
async def api_update_valid_contact(contact_id):
    """Atualiza um contato da lista de válidos e o revalida."""
    try:
        data = await request.json
        new_name = data.get('name')
        new_number = str(data.get('numero', ''))

        if not new_name or not new_number:
            return jsonify({'success': False, 'error': 'Nome e número são obrigatórios.'}), 400

        # Encontrar o contato na lista principal (fonte da verdade)
        contact_to_update = next((c for c in app_state['contacts'] if c.get('id') == contact_id), None)

        if not contact_to_update:
            return jsonify({'success': False, 'error': 'Contato não encontrado.'}), 404

        # Atualizar dados no contato principal
        contact_to_update['nome'] = new_name
        contact_to_update['numero'] = new_number

        # Revalidar o número
        is_valid_now = validate_phone_number(new_number)

        # Atualizar as listas de válidos e inválidos
        app_state['valid_contacts'] = [c for c in app_state['valid_contacts'] if c.get('id') != contact_id]
        app_state['invalid_contacts'] = [c for c in app_state['invalid_contacts'] if c.get('id') != contact_id]

        if is_valid_now:
            contact_to_update['status'] = 'Válido'
            contact_to_update['status_class'] = 'success'
            app_state['valid_contacts'].append(contact_to_update)
            add_log(f"🔄 Contato ID {contact_id} atualizado e validado com sucesso.")
        else:
            contact_to_update['status'] = 'Inválido'
            contact_to_update['status_class'] = 'danger'
            app_state['invalid_contacts'].append(contact_to_update)
            add_log(f"🔄 Contato ID {contact_id} atualizado e agora é inválido.")

        # Ordenar listas para manter consistência, se necessário (opcional)
        app_state['valid_contacts'].sort(key=lambda c: c.get('id', 0))
        app_state['invalid_contacts'].sort(key=lambda c: c.get('id', 0))

        return jsonify({
            'success': True,
            'contact': contact_to_update,
            'stats': {
                'total': len(app_state['contacts']),
                'valid': len(app_state['valid_contacts']),
                'invalid': len(app_state['invalid_contacts'])
            }
        })

    except Exception as e:
        error_msg = f"Erro ao atualizar contato: {str(e)}"
        add_log(f"❌ {error_msg}")
        return jsonify({'success': False, 'error': error_msg}), 500


@app.route('/api/validate_contacts', methods=['POST'])
def api_validate_contacts():
    """Validar e formatar números de telefone, e atualizar estado global"""
    try:
        if not app_state.get('contacts'):
            return jsonify({'success': False, 'error': 'Nenhum contato carregado para validar.'})

        app_state['valid_contacts'] = []
        app_state['invalid_contacts'] = []

        for index, contact in enumerate(app_state['contacts']):
            contact['id'] = index
            original_number = str(contact.get('numero', ''))
            
            formatted_number = validate_phone_number(original_number)
            
            if formatted_number:
                contact['numero'] = formatted_number
                contact['status'] = 'Válido'
                contact['status_class'] = 'success'
                app_state['valid_contacts'].append(contact)
            else:
                contact['status'] = 'Inválido'
                contact['status_class'] = 'danger'
                app_state['invalid_contacts'].append(contact)
        
        valid_count = len(app_state['valid_contacts'])
        invalid_count = len(app_state['invalid_contacts'])
        
        add_log(f"✅ Validação e formatação concluídas: {valid_count} válidos, {invalid_count} inválidos")
        
        # Retornar todos os contatos com o novo status para a UI
        all_contacts = app_state['valid_contacts'] + app_state['invalid_contacts']
        # Ordenar por ID para manter a ordem original
        all_contacts.sort(key=lambda x: x['id'])

        return jsonify({
            'success': True,
            'stats': {
                'total': len(app_state['contacts']),
                'valid': valid_count,
                'invalid': invalid_count
            },
            'contacts': all_contacts,
            'message': f'Validação concluída: {valid_count} válidos, {invalid_count} inválidos.'
        })
        
    except Exception as e:
        error_msg = f"Erro durante a validação dos contatos: {str(e)}"
        add_log(f"❌ {error_msg}")
        app_state['valid_contacts'] = []
        app_state['invalid_contacts'] = []
        return jsonify({'success': False, 'error': error_msg})




@app.route('/api/update_contact', methods=['POST'])
async def api_update_contact():
    """Atualiza e revalida um contato específico"""
    try:
        data = await request.json
        contact_id = data.get('id')
        new_name = data.get('nome')
        new_number = str(data.get('numero', ''))

        if contact_id is None:
            return jsonify({'success': False, 'error': 'ID do contato não fornecido'}), 400

        # Encontrar o contato na lista principal
        contact_to_update = next((c for c in app_state['contacts'] if c.get('id') == contact_id), None)

        if not contact_to_update:
            return jsonify({'success': False, 'error': 'Contato não encontrado'}), 404

        # Atualizar dados
        contact_to_update['nome'] = new_name
        contact_to_update['numero'] = new_number

        # Revalidar o contato
        is_valid_now = validate_phone_number(new_number)

        # Atualizar listas de válidos/inválidos
        # Remover de ambas as listas primeiro para evitar duplicatas
        app_state['valid_contacts'] = [c for c in app_state['valid_contacts'] if c.get('id') != contact_id]
        app_state['invalid_contacts'] = [c for c in app_state['invalid_contacts'] if c.get('id') != contact_id]

        if is_valid_now:
            app_state['valid_contacts'].append(contact_to_update)
            add_log(f"🔄 Contato {contact_id} atualizado e agora é VÁLIDO.")
        else:
            app_state['invalid_contacts'].append(contact_to_update)
            add_log(f"🔄 Contato {contact_id} atualizado e continua INVÁLIDO.")

        return jsonify({
            'success': True,
            'is_valid': is_valid_now,
            'stats': {
                'total': len(app_state['contacts']),
                'valid': len(app_state['valid_contacts']),
                'invalid': len(app_state['invalid_contacts'])
            }
        })

    except Exception as e:
        error_msg = f"Erro ao atualizar contato: {str(e)}"
        add_log(f"❌ {error_msg}")
        return jsonify({'success': False, 'error': error_msg}), 500


@app.route('/api/invalid_contacts')
def api_get_invalid_contacts():
    """Retorna a lista de contatos inválidos"""
    try:
        return jsonify({
            'success': True,
            'contacts': app_state.get('invalid_contacts', [])
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/start_sending', methods=['POST'])
async def api_start_sending():
    """Iniciar envio de sequência de mensagens para contatos selecionados"""
    try:
        data = await request.json
        contact_ids = data.get('contact_ids')  # Lista de IDs dos contatos selecionados

        if not app_state['config']:
            return jsonify({'success': False, 'error': 'Configure a API primeiro'})

        if not app_state['valid_contacts']:
            return jsonify({'success': False, 'error': 'Carregue e valide os contatos primeiro'})

        sequence = app_state['message_config'].get('sequence', [])
        if not sequence:
            return jsonify({'success': False, 'error': 'Configure a sequência de mensagens primeiro'})

        if app_state['sending_active']:
            return jsonify({'success': False, 'error': 'Envio já está em andamento'})

        # Filtrar contatos a serem enviados
        if contact_ids:
            # Converter contact_ids para inteiros para comparação correta
            contact_ids_int = []
            for cid in contact_ids:
                try:
                    contact_ids_int.append(int(cid))
                except (ValueError, TypeError):
                    continue
            contacts_to_send = [c for c in app_state['valid_contacts'] if c.get('id') in contact_ids_int]
        else:
            # Se nenhum ID for fornecido, enviar para todos os válidos (comportamento padrão)
            contacts_to_send = app_state['valid_contacts']

        if not contacts_to_send:
            return jsonify({'success': False, 'error': 'Nenhum contato válido selecionado para envio.'})

        total_messages = len(contacts_to_send) * len(sequence)

        app_state['send_progress'] = {
            'current': 0,
            'total': total_messages,
            'success': 0,
            'error': 0,
            'current_contact': '',
            'current_message': 1,
            'sequence_length': len(sequence)
        }

        app_state['sending_active'] = True

        # Passar a lista de contatos para a thread
        send_thread = threading.Thread(target=send_messages_thread, args=(contacts_to_send,))
        send_thread.daemon = True
        send_thread.start()

        add_log(f"🚀 Iniciando envio: {len(sequence)} mensagens para {len(contacts_to_send)} contatos selecionados")

        return jsonify({'success': True, 'message': 'Envio iniciado!'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/stop_sending', methods=['POST'])
def api_stop_sending():
    """Parar envio"""
    try:
        app_state['sending_active'] = False
        add_log("⏸️ Envio pausado pelo usuário")
        return jsonify({'success': True, 'message': 'Envio pausado'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/logs')
def api_logs():
    """Obter logs do sistema"""
    try:
        return jsonify({'success': True, 'logs': app_state['logs']})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/create_sample')
def api_create_sample():
    """Criar planilha de exemplo"""
    try:
        sample_path = 'sample_contacts.xlsx'
        create_sample_excel(sample_path)
        
        add_log("📋 Planilha de exemplo criada")
        
        return send_file(sample_path, as_attachment=True, download_name='sample_contacts.xlsx')
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


def send_messages_thread(contacts_to_send):
    """Thread para envio de sequência de mensagens com intervalos ultra-humanizados"""
    try:
        app_state['sender'] = WhatsAppAPISender(app_state['config'])
        
        sequence = app_state['message_config'].get('sequence', [])
        base_sequence_interval = int(app_state['message_config'].get('interval', 10))
        
        if not sequence:
            add_log("❌ Nenhuma sequência de mensagens configurada")
            app_state['sending_active'] = False
            return
        
        total_messages = len(contacts_to_send) * len(sequence)
        
        add_log(f"🚀 Thread de envio iniciada para {len(contacts_to_send)} contatos.")
        
        # Perfis de comportamento humano
        behavior_profiles = {
            'conservador': {'base_mult': 1.5, 'variance': 0.4, 'fatigue_factor': 1.1},
            'normal': {'base_mult': 1.0, 'variance': 0.6, 'fatigue_factor': 1.2},
            'agressivo': {'base_mult': 0.7, 'variance': 0.8, 'fatigue_factor': 1.3}
        }
        
        # Selecionar perfil aleatório
        profile_name = random.choice(list(behavior_profiles.keys()))
        profile = behavior_profiles[profile_name]
        add_log(f"🎭 Perfil de comportamento: {profile_name}")
        
        message_count = 0
        session_start_time = time.time()
        
        for contact_idx, contact in enumerate(contacts_to_send):
            if not app_state['sending_active']:
                add_log("⏸️ Envio pausado pelo usuário")
                break
            
            numero = contact['numero']
            nome = contact.get('nome', app_state['message_config']['fallback_name'])
            
            add_log(f"👤 Processando {nome} ({numero}) - Sequência de {len(sequence)} mensagens")
            
            # Simular "pensamento" antes de iniciar contato
            if contact_idx > 0:  # Não na primeira vez
                thinking_time = random.uniform(1, 4)
                add_log(f"🤔 Preparando próximo contato... {thinking_time:.1f}s")
                time.sleep(thinking_time)
            
            # Enviar cada mensagem da sequência para este contato
            for msg_idx, message in enumerate(sequence):
                if not app_state['sending_active']:
                    break
                
                message_count += 1
                
                # Atualizar progresso
                app_state['send_progress']['current'] = message_count
                app_state['send_progress']['current_contact'] = f"{nome} ({numero})"
                app_state['send_progress']['current_message'] = msg_idx + 1
                
                # Simular "digitação" ou "preparação" da mensagem
                if msg_idx > 0:  # Não na primeira mensagem do contato
                    prep_time = random.uniform(0.5, 2.5)
                    if random.random() < 0.15:  # 15% chance de pausar mais (hesitação)
                        prep_time += random.uniform(1, 3)
                        add_log(f"⏸️ Hesitando... {prep_time:.1f}s")
                    time.sleep(prep_time)
                
                try:
                    success = False
                    
                    if message['type'] == 'text':
                        # Mensagem de texto
                        texto = message['content'].replace('{nome}', nome)
                        add_log(f"📤 Enviando mensagem {msg_idx + 1}/{len(sequence)} (texto) para {nome}")
                        
                        # Simular tempo de digitação baseado no tamanho da mensagem
                        typing_time = len(texto) * random.uniform(0.02, 0.08)  # ~20-80ms por caractere
                        typing_time = min(typing_time, 5)  # Máximo 5 segundos
                        if typing_time > 1:
                            add_log(f"⌨️ Digitando... {typing_time:.1f}s")
                            time.sleep(typing_time)
                        
                        success = app_state['sender'].send_message(numero, texto, '')
                        
                    elif message['type'] == 'media':
                        # Mensagem de mídia
                        caminho_midia = message['path']
                        legenda = message.get('caption', '').replace('{nome}', nome) if message.get('caption') else ''
                        
                        add_log(f"📤 Enviando mensagem {msg_idx + 1}/{len(sequence)} ({message['mediaType']}) para {nome}")
                        
                        # Simular tempo de seleção/upload de mídia
                        media_time = random.uniform(2, 6)
                        add_log(f"📎 Preparando mídia... {media_time:.1f}s")
                        time.sleep(media_time)
                        
                        success = app_state['sender'].send_message(numero, legenda, caminho_midia)
                    
                    if success:
                        app_state['send_progress']['success'] += 1
                        add_log(f"✅ Mensagem {msg_idx + 1} enviada para {nome}")
                    else:
                        app_state['send_progress']['error'] += 1
                        add_log(f"❌ Falha na mensagem {msg_idx + 1} para {nome}")
                
                except Exception as e:
                    app_state['send_progress']['error'] += 1
                    add_log(f"❌ Erro na mensagem {msg_idx + 1} para {nome}: {str(e)}")
                
                # Sistema avançado de intervalos humanizados
                if app_state['sending_active']:
                    
                    # Calcular fadiga da sessão (intervalos aumentam com o tempo)
                    session_duration = (time.time() - session_start_time) / 60  # em minutos
                    fatigue_multiplier = 1 + (session_duration * profile['fatigue_factor'] * 0.1)
                    
                    if msg_idx < len(sequence) - 1:
                        # ===== INTERVALO ENTRE MENSAGENS DA SEQUÊNCIA =====
                        # Usar perfil de comportamento
                        base_time = base_sequence_interval * profile['base_mult']
                        
                        # Variação principal (±variance%)
                        variance = random.uniform(-profile['variance'], profile['variance'])
                        varied_time = base_time * (1 + variance)
                        
                        # Aplicar fadiga
                        fatigued_time = varied_time * fatigue_multiplier
                        
                        # Adicionar micro-variações (simulando inconsistência humana)
                        micro_variation = random.uniform(-0.3, 0.3)
                        final_time = fatigued_time * (1 + micro_variation)
                        
                        # Ocasionalmente pausas mais longas (pessoa se distrai)
                        if random.random() < 0.12:  # 12% chance
                            distraction_time = random.uniform(5, 15)
                            final_time += distraction_time
                            add_log(f"😴 Pausa de distração... {distraction_time:.1f}s extra")
                        
                        # Mínimo e máximo realistas
                        wait_time = max(1, min(final_time, 120))  # Entre 1s e 2min
                        
                        add_log(f"⏳ Aguardando {wait_time:.1f}s antes da próxima mensagem...")
                        time.sleep(wait_time)
            
            # INTERVALO ENTRE CONTATOS (após completar toda a sequência)
            if app_state['sending_active'] and contact_idx < len(contacts_to_send) - 1:
                # ===== INTERVALO ENTRE CONTATOS =====
                config_min = int(app_state['config'].get('min_interval_seconds', 15))
                config_max = int(app_state['config'].get('max_interval_seconds', 30))
                
                # Calcular fadiga da sessão
                session_duration = (time.time() - session_start_time) / 60  # em minutos
                fatigue_multiplier = 1 + (session_duration * profile['fatigue_factor'] * 0.1)
                
                # Perfil de comportamento para intervalos entre contatos
                profile_min = config_min * profile['base_mult']
                profile_max = config_max * profile['base_mult']
                
                # Variação principal
                variance = random.uniform(-profile['variance'] * 0.5, profile['variance'])
                varied_min = profile_min * (1 + variance)
                varied_max = profile_max * (1 + variance)
                
                # Garantir ordem lógica
                if varied_min > varied_max:
                    varied_min, varied_max = varied_max, varied_min
                
                # Aplicar fadiga
                fatigued_min = varied_min * fatigue_multiplier
                fatigued_max = varied_max * fatigue_multiplier
                
                # Selecionar tempo aleatório no range
                wait_time = random.uniform(fatigued_min, fatigued_max)
                
                # Padrões especiais de comportamento humano
                random_behavior = random.random()
                
                if random_behavior < 0.05:  # 5% - Pressa súbita
                    wait_time *= random.uniform(0.3, 0.6)
                    add_log(f"🏃‍♂️ Acelerando ritmo...")
                elif random_behavior < 0.15:  # 10% - Pausa longa
                    extra_time = random.uniform(20, 60)
                    wait_time += extra_time
                    add_log(f"☕ Pausa longa... +{extra_time:.1f}s")
                elif random_behavior < 0.25:  # 10% - Ritmo irregular
                    wait_time *= random.uniform(0.7, 1.4)
                    add_log(f"🎲 Ritmo irregular...")
                
                # Pausas por "blocos de tempo" (simula horários de trabalho)
                hour = datetime.now().hour
                if hour in [12, 13] or hour in [17, 18, 19]:  # Horário de almoço/jantar
                    if random.random() < 0.3:  # 30% chance
                        meal_pause = random.uniform(10, 30)
                        wait_time += meal_pause
                        add_log(f"🍽️ Pausa para refeição... +{meal_pause:.1f}s")
                
                # Limites finais
                wait_time = max(3, min(wait_time, 300))  # Entre 3s e 5min
                
                # Log final com contexto
                log_msg = f"⏳ Aguardando {wait_time:.1f}s antes do próximo contato"
                if fatigue_multiplier > 1.3:
                    log_msg += " (fadiga detectada)"
                add_log(log_msg)
                
                time.sleep(wait_time)
        
        # Finalizar envio
        app_state['sending_active'] = False
        
        success_count = app_state['send_progress']['success']
        error_count = app_state['send_progress']['error']
        total_count = app_state['send_progress']['total']
        
        success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
        
        session_duration = (time.time() - session_start_time) / 60
        
        add_log("=" * 50)
        add_log("🎉 SEQUÊNCIA CONCLUÍDA!")
        add_log(f"✅ Sucessos: {success_count}")
        add_log(f"❌ Erros: {error_count}")
        add_log(f"📈 Taxa de sucesso: {success_rate:.1f}%")
        add_log(f"⏱️ Duração da sessão: {session_duration:.1f} minutos")
        add_log(f"🎭 Perfil usado: {profile_name}")
        
    except Exception as e:
        app_state['sending_active'] = False
        add_log(f"💥 Erro crítico no envio: {str(e)}")
        
    finally:
        app_state['send_progress']['current_contact'] = 'Envio finalizado'


def get_media_icon(media_type):
    """Retorna ícone para tipo de mídia"""
    icons = {
        'image': '📷',
        'video': '🎥',
        'audio': '🎵',
        'document': '📄'
    }
    return icons.get(media_type, '📎')


def add_log(message):
    """Adicionar mensagem ao log"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = {
        'timestamp': timestamp,
        'message': message
    }
    app_state['logs'].append(log_entry)
    
    # Manter apenas os últimos 1000 logs
    if len(app_state['logs']) > 1000:
        app_state['logs'] = app_state['logs'][-500:]  # Reduzir para 500


def load_initial_config():
    """Carregar configuração inicial"""
    try:
        app_state['config'] = load_config()
        add_log("✅ Configuração carregada do config.json")
    except Exception as e:
        add_log(f"⚠️ Erro ao carregar configuração: {str(e)}")


def open_browser():
    """Abrir navegador automaticamente"""
    webbrowser.open('http://127.0.0.1:5000')


@app.route('/api/upload_media', methods=['POST'])
async def upload_media():
    """Upload de arquivo de mídia"""
    try:
        files = await request.files
        if 'file' not in files:
            return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'})
        
        file = files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado'})
        
        # Validar tipo de arquivo
        allowed_extensions = {
            'image': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
            'video': ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv'],
            'audio': ['mp3', 'wav', 'ogg', 'aac', 'm4a', 'flac'],
            'document': ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'rtf']
        }
        
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        is_valid = any(file_ext in extensions for extensions in allowed_extensions.values())
        
        if not is_valid:
            return jsonify({'success': False, 'message': 'Tipo de arquivo não suportado'})
        
        # Gerar nome único para o arquivo
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        unique_filename = f"{timestamp}_{name}{ext}"
        
        # Salvar arquivo
        media_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'media')
        os.makedirs(media_folder, exist_ok=True)
        
        filepath = os.path.join(media_folder, unique_filename)
        await file.save(str(filepath))
        
        # Retornar caminho relativo
        relative_path = os.path.join('uploads', 'media', unique_filename).replace('\\', '/')
        
        add_log(f"📁 Arquivo enviado: {unique_filename}")
        
        return jsonify({
            'success': True,
            'filepath': relative_path,
            'filename': unique_filename,
            'original_name': file.filename
        })
        
    except Exception as e:
        add_log(f"❌ Erro no upload: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/save_template', methods=['POST'])
async def save_template():
    """Salvar template de sequência"""
    try:
        data = await request.get_json()
        template_name = data.get('name', '').strip()
        sequence_data = data.get('sequence', {})
        
        if not template_name:
            return jsonify({'success': False, 'message': 'Nome do template é obrigatório'})
        
        if not sequence_data.get('sequence'):
            return jsonify({'success': False, 'message': 'Sequência não pode estar vazia'})
        
        # Sanitizar nome do arquivo
        safe_name = "".join(c for c in template_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_name}.json"
        filepath = os.path.join(TEMPLATES_FOLDER, filename)
        
        # Preparar dados do template
        template_data = {
            'name': template_name,
            'created_at': datetime.now().isoformat(),
            'sequence': sequence_data.get('sequence', []),
            'interval': sequence_data.get('interval', 10),
            'fallback_name': sequence_data.get('fallback_name', 'amigo(a)')
        }
        
        # Salvar arquivo
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, ensure_ascii=False, indent=2)
        
        add_log(f"💾 Template salvo: {template_name}")
        
        return jsonify({'success': True, 'message': 'Template salvo com sucesso'})
        
    except Exception as e:
        add_log(f"❌ Erro ao salvar template: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/get_templates', methods=['GET'])
def get_templates():
    """Obter lista de templates salvos"""
    try:
        templates = []
        
        if os.path.exists(TEMPLATES_FOLDER):
            for filename in os.listdir(TEMPLATES_FOLDER):
                if filename.endswith('.json'):
                    filepath = os.path.join(TEMPLATES_FOLDER, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            template_data = json.load(f)
                            templates.append({
                                'name': template_data.get('name', filename[:-5]),
                                'created_at': template_data.get('created_at', ''),
                                'message_count': len(template_data.get('sequence', []))
                            })
                    except Exception as e:
                        add_log(f"⚠️ Erro ao ler template {filename}: {str(e)}")
                        continue
        
        # Ordenar por data de criação (mais recente primeiro)
        templates.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return jsonify({'success': True, 'templates': templates})
        
    except Exception as e:
        add_log(f"❌ Erro ao listar templates: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/load_template/<template_name>', methods=['GET'])
def load_template(template_name):
    """Carregar template específico"""
    try:
        # Procurar arquivo do template
        template_file = None
        if os.path.exists(TEMPLATES_FOLDER):
            for filename in os.listdir(TEMPLATES_FOLDER):
                if filename.endswith('.json'):
                    filepath = os.path.join(TEMPLATES_FOLDER, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            template_data = json.load(f)
                            if template_data.get('name') == template_name:
                                template_file = template_data
                                break
                    except Exception:
                        continue
        
        if not template_file:
            return jsonify({'success': False, 'message': 'Template não encontrado'})
        
        add_log(f"📂 Template carregado: {template_name}")
        
        return jsonify({
            'success': True,
            'template': {
                'sequence': template_file.get('sequence', []),
                'interval': template_file.get('interval', 10),
                'fallback_name': template_file.get('fallback_name', 'amigo(a)')
            }
        })
        
    except Exception as e:
        add_log(f"❌ Erro ao carregar template: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})





# Variável global para armazenar o QR code
qr_code_data = None

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook para receber eventos do WAHA"""
    global qr_code_data
    try:
        data = request.get_json()
        print(f"📥 Webhook recebido: {data}")
        
        # Verificar se é um evento de QR code
        if data.get('event') == 'auth.qr':
            qr_code_data = data.get('payload', {}).get('qr')
            print(f"📱 QR Code recebido via webhook!")
            
        return jsonify({'status': 'ok'})
    except Exception as e:
        print(f"❌ Erro no webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/qr')
def get_qr():
    """Endpoint para obter o QR code"""
    global qr_code_data
    if qr_code_data:
        return jsonify({'qr': qr_code_data})
    else:
        return jsonify({'error': 'QR code não disponível'}), 404

@app.route('/qr_page')
def qr_page():
    """Página para exibir o QR code"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>QR Code WhatsApp</title>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 20px; }
            #qr-container { margin: 20px auto; }
            #qr-image { max-width: 300px; border: 2px solid #25D366; padding: 10px; }
            .status { margin: 10px; padding: 10px; border-radius: 5px; }
            .waiting { background-color: #fff3cd; color: #856404; }
            .error { background-color: #f8d7da; color: #721c24; }
        </style>
    </head>
    <body>
        <h1>🔗 Conectar WhatsApp</h1>
        <div id="status" class="status waiting">Aguardando QR Code...</div>
        <div id="qr-container">
            <img id="qr-image" style="display: none;" />
        </div>
        <button onclick="checkQR()">🔄 Verificar QR Code</button>
        
        <script>
            function checkQR() {
                fetch('/qr')
                    .then(response => response.json())
                    .then(data => {
                        if (data.qr) {
                            document.getElementById('qr-image').src = data.qr;
                            document.getElementById('qr-image').style.display = 'block';
                            document.getElementById('status').innerHTML = '📱 Escaneie o QR Code com seu WhatsApp';
                            document.getElementById('status').className = 'status waiting';
                        } else {
                            document.getElementById('status').innerHTML = '❌ QR Code não disponível';
                            document.getElementById('status').className = 'status error';
                        }
                    })
                    .catch(error => {
                        document.getElementById('status').innerHTML = '❌ Erro ao obter QR Code';
                        document.getElementById('status').className = 'status error';
                    });
            }
            
            // Verificar QR code automaticamente a cada 3 segundos
            setInterval(checkQR, 3000);
            checkQR(); // Verificar imediatamente
        </script>
    </body>
    </html>
    '''

# WAHA Proxy Routes (baseado na aplicação de referência)
WAHA_BASE_URL = 'http://localhost:3000'
WAHA_API_KEY = 'waha-key-2025'

@app.route('/api/waha/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
async def waha_proxy(path):
    """Proxy para API do WAHA - evita problemas de CORS"""
    try:
        url = f"{WAHA_BASE_URL}/api/{path}"
        method = request.method
        
        # Preparar headers
        headers = {
            'X-Api-Key': WAHA_API_KEY,
            'Content-Type': 'application/json'
        }
        
        # Obter dados do request se for POST/PUT
        data = None
        if method in ['POST', 'PUT']:
            try:
                data = await request.get_json()
            except:
                pass
        
        # Fazer requisição para WAHA
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_data = await response.text()
                
                # Tentar parsear como JSON
                try:
                    response_json = json.loads(response_data)
                    return jsonify(response_json), response.status
                except:
                    return response_data, response.status
                    
    except Exception as e:
        return jsonify({'error': f'Erro no proxy WAHA: {str(e)}'}), 500

@app.route('/api/waha/qr/<session_name>', methods=['GET'])
async def get_waha_qr_code(session_name):
    """Endpoint específico para obter QR code do WAHA"""
    try:
        url = f"{WAHA_BASE_URL}/api/{session_name}/auth/qr"
        
        headers = {
            'X-Api-Key': WAHA_API_KEY,
            'Accept': 'image/png'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    image_data = await response.read()
                    qr_base64 = base64.b64encode(image_data).decode('utf-8')
                    
                    return jsonify({
                        'success': True,
                        'qr_code': qr_base64,
                        'content_type': response.headers.get('content-type', 'image/png')
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': f'WAHA retornou status {response.status}'
                    }), response.status
                    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao obter QR code: {str(e)}'
        }), 500

@app.route('/api/waha/session/status/<session_name>', methods=['GET'])
async def get_waha_session_status(session_name):
    """Verifica status da sessão WAHA"""
    try:
        url = f"{WAHA_BASE_URL}/api/sessions/{session_name}"
        
        headers = {
            'X-Api-Key': WAHA_API_KEY,
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    return jsonify({
                        'success': True,
                        'status': data.get('status', 'UNKNOWN'),
                        'data': data
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': f'Sessão não encontrada ou erro no WAHA (status {response.status})'
                    }), response.status
                    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao verificar status: {str(e)}'
        }), 500

@app.route('/api/waha/session/start', methods=['POST'])
async def start_waha_session():
    """Inicia uma nova sessão WAHA"""
    try:
        data = await request.get_json() or {}
        session_name = data.get('session', 'default')
        
        url = f"{WAHA_BASE_URL}/api/sessions/start"
        
        headers = {
            'X-Api-Key': WAHA_API_KEY,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'name': session_name,
            'config': {
                'proxy': None,
                'webhooks': []
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as response:
                response_data = await response.json()
                
                if response.status in [200, 201]:
                    return jsonify({
                        'success': True,
                        'message': 'Sessão iniciada com sucesso',
                        'data': response_data
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': f'Erro ao iniciar sessão: {response_data.get("message", "Erro desconhecido")}'
                    }), response.status
                    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao iniciar sessão: {str(e)}'
        }), 500

# WhatsApp Web (Playwright) Routes
@app.route('/api/whatsapp/qr_code', methods=['POST'])
async def get_whatsapp_qr_code():
    # Garante que a sessão esteja iniciada apenas se não estiver ativa
    if not whatsapp_manager.browser:
        success = await whatsapp_manager.start_session()
        if not success:
            return jsonify({'success': False, 'error': 'Failed to start WhatsApp Web session.'}), 500

    qr_base64, error = await whatsapp_manager.get_qr_code()
    if error:
        return jsonify({'success': False, 'error': error}), 500
    
    return jsonify({'success': True, 'qr_code': qr_base64})


@app.route('/api/waha/qr_screenshot', methods=['POST'])
async def get_waha_qr_screenshot():
    """Captura screenshot do QR code do dashboard WAHA usando Playwright"""
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            # Usar Chromium em modo headless
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720}
            )
            page = await context.new_page()
            
            try:
                # Navegar para o dashboard WAHA
                await page.goto('http://localhost:3000/dashboard/', wait_until='networkidle')
                
                # Aguardar mais tempo para a SPA carregar completamente
                await page.wait_for_timeout(8000)
                
                # Aguardar que o loading desapareça
                try:
                    await page.wait_for_selector('#loading-body', state='hidden', timeout=10000)
                except:
                    pass  # Se não encontrar o loading, continua
                
                # Aguardar mais um pouco após o loading
                await page.wait_for_timeout(3000)
                
                # Tentar encontrar o QR code usando diferentes seletores
                qr_selectors = [
                    'canvas',  # QR code geralmente é renderizado em canvas
                    '[data-testid="qr-code"]',
                    '.qr-code',
                    '#qr-code',
                    'img[alt*="QR"]',
                    'img[src*="qr"]',
                    'svg',  # QR code pode ser SVG
                    '.p-image',  # PrimeVue image component
                    '[role="img"]'  # Elementos com role de imagem
                ]
                
                qr_element = None
                for selector in qr_selectors:
                    try:
                        qr_element = await page.wait_for_selector(selector, timeout=3000)
                        if qr_element:
                            break
                    except:
                        continue
                
                if qr_element:
                    # Capturar screenshot do elemento QR code
                    screenshot_bytes = await qr_element.screenshot()
                    qr_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
                    
                    await browser.close()
                    return jsonify({
                        'success': True,
                        'qr_code': qr_base64
                    })
                else:
                    # Se não encontrar QR code específico, capturar página completa para debug
                    full_screenshot = await page.screenshot(full_page=True)
                    
                    # Salvar screenshot completo para debug
                    with open('debug_full_page.png', 'wb') as f:
                        f.write(full_screenshot)
                    
                    # Capturar área central da página
                    screenshot_bytes = await page.screenshot(
                        clip={'x': 400, 'y': 200, 'width': 400, 'height': 400}
                    )
                    qr_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
                    
                    # Obter HTML da página para debug
                    page_content = await page.content()
                    with open('debug_page_content.html', 'w', encoding='utf-8') as f:
                        f.write(page_content)
                    
                    await browser.close()
                    return jsonify({
                        'success': True,
                        'qr_code': qr_base64,
                        'note': 'QR code específico não encontrado, capturada área central. Debug: debug_full_page.png e debug_page_content.html salvos'
                    })
                    
            except Exception as e:
                await browser.close()
                return jsonify({
                    'success': False,
                    'error': f'Erro ao capturar QR code: {str(e)}'
                }), 500
                
    except ImportError:
        return jsonify({
            'success': False,
            'error': 'Playwright não está instalado. Execute: pip install playwright && playwright install'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500







def find_available_port():
    """Encontra uma porta disponível"""
    import socket
    ports_to_try = [5000, 5001, 5002, 5003, 8000, 8080]
    
    for port in ports_to_try:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None

def main():
    """Função principal da aplicação web"""
    setup_logging()
    load_initial_config()
    
    # Encontrar porta disponível
    port = find_available_port()
    
    if port is None:
        print("❌ Não foi possível encontrar uma porta disponível")
        return
    
    print("🌐 WhatsApp API Sender - Interface Web")
    print("=" * 50)
    print("🚀 Iniciando servidor web...")
    print(f"📱 Acesse: http://127.0.0.1:{port}")
    print("⏹️  Pressione Ctrl+C para parar")
    print("=" * 50)
    
    import asyncio
    from hypercorn.config import Config
    from hypercorn.asyncio import serve

    config = Config()
    config.bind = [f"127.0.0.1:{port}"]
    config.use_reloader = False
    
    try:
        asyncio.run(serve(app, config))
    except KeyboardInterrupt:
        print("\nServidor interrompido.")


if __name__ == '__main__':
    main()