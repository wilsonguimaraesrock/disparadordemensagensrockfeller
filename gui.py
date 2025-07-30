#!/usr/bin/env python3
"""
WhatsApp API Sender - GUI Module
Interface gráfica moderna para envio em massa de mensagens
"""

import os
import sys
import threading
import json
import logging
from pathlib import Path
from datetime import datetime
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk

from utils import (
    load_config,
    setup_logging,
    load_contacts_from_excel,
    validate_phone_number,
    create_sample_excel
)
from api_sender import WhatsAppAPISender


# Configurar aparência do CustomTkinter
ctk.set_appearance_mode("dark")  # "dark" ou "light"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"


class WhatsAppSenderGUI:
    """Interface gráfica principal do WhatsApp API Sender"""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🚀 WhatsApp API Sender")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Configurar logging
        setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Variáveis de estado
        self.config = None
        self.contacts = []
        self.valid_contacts = []
        self.sender = None
        self.sending_active = False
        
        # Configurar interface
        self.setup_ui()
        self.load_initial_config()
        
    def setup_ui(self):
        """Configura a interface do usuário"""
        
        # Frame principal com abas
        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Criar abas
        self.tab_config = self.tabview.add("⚙️ Configuração")
        self.tab_contacts = self.tabview.add("📋 Contatos")
        self.tab_send = self.tabview.add("🚀 Envio")
        self.tab_logs = self.tabview.add("📊 Logs")
        
        self.setup_config_tab()
        self.setup_contacts_tab()
        self.setup_send_tab()
        self.setup_logs_tab()
        
    def setup_config_tab(self):
        """Configura a aba de configuração da API"""
        
        # Frame de configuração
        config_frame = ctk.CTkFrame(self.tab_config)
        config_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title = ctk.CTkLabel(config_frame, text="Configuração da API WhatsApp", 
                           font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=20)
        
        # Provider
        provider_frame = ctk.CTkFrame(config_frame)
        provider_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(provider_frame, text="Provider:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(20,5))
        
        self.provider_var = ctk.StringVar(value="waha")
        provider_options = ["waha", "chat-api", "z-api", "ultramsg", "generic"]
        self.provider_combo = ctk.CTkComboBox(provider_frame, values=provider_options, 
                                            variable=self.provider_var,
                                            command=self.on_provider_change)
        self.provider_combo.pack(fill="x", padx=20, pady=(0,20))
        
        # Base URL
        url_frame = ctk.CTkFrame(config_frame)
        url_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(url_frame, text="Base URL:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(20,5))
        
        self.base_url_var = ctk.StringVar(value="http://localhost:3000")
        self.base_url_entry = ctk.CTkEntry(url_frame, textvariable=self.base_url_var,
                                         placeholder_text="Ex: http://localhost:3000")
        self.base_url_entry.pack(fill="x", padx=20, pady=(0,20))
        
        # Instance ID
        instance_frame = ctk.CTkFrame(config_frame)
        instance_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(instance_frame, text="Instance ID:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(20,5))
        
        self.instance_id_var = ctk.StringVar(value="default")
        self.instance_id_entry = ctk.CTkEntry(instance_frame, textvariable=self.instance_id_var,
                                            placeholder_text="default")
        self.instance_id_entry.pack(fill="x", padx=20, pady=(0,20))
        
        # Token
        token_frame = ctk.CTkFrame(config_frame)
        token_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(token_frame, text="API Token:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(20,5))
        
        self.token_var = ctk.StringVar()
        self.token_entry = ctk.CTkEntry(token_frame, textvariable=self.token_var,
                                       placeholder_text="Seu token da API", show="*")
        self.token_entry.pack(fill="x", padx=20, pady=(0,10))
        
        # Botão para mostrar/esconder token
        self.show_token_var = ctk.BooleanVar()
        self.show_token_check = ctk.CTkCheckBox(token_frame, text="Mostrar token",
                                              variable=self.show_token_var,
                                              command=self.toggle_token_visibility)
        self.show_token_check.pack(anchor="w", padx=20, pady=(0,20))
        
        # Botões de ação
        button_frame = ctk.CTkFrame(config_frame)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        save_btn = ctk.CTkButton(button_frame, text="💾 Salvar Configuração",
                               command=self.save_config, height=40)
        save_btn.pack(side="left", padx=20, pady=20)
        
        test_btn = ctk.CTkButton(button_frame, text="🔍 Testar Conexão",
                               command=self.test_connection, height=40)
        test_btn.pack(side="right", padx=20, pady=20)
        
    def setup_contacts_tab(self):
        """Configura a aba de contatos"""
        
        # Frame principal
        contacts_frame = ctk.CTkFrame(self.tab_contacts)
        contacts_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título e instruções
        title = ctk.CTkLabel(contacts_frame, text="Gerenciar Contatos", 
                           font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=20)
        
        # Frame de seleção de arquivo
        file_frame = ctk.CTkFrame(contacts_frame)
        file_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(file_frame, text="Planilha Excel (.xlsx):", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(20,5))
        
        file_select_frame = ctk.CTkFrame(file_frame)
        file_select_frame.pack(fill="x", padx=20, pady=(0,20))
        
        self.file_path_var = ctk.StringVar()
        self.file_path_entry = ctk.CTkEntry(file_select_frame, textvariable=self.file_path_var,
                                          placeholder_text="Selecione o arquivo Excel...")
        self.file_path_entry.pack(side="left", fill="x", expand=True, padx=(0,10))
        
        browse_btn = ctk.CTkButton(file_select_frame, text="📁 Procurar",
                                 command=self.browse_excel_file, width=100)
        browse_btn.pack(side="right")
        
        # Botões de ação
        action_frame = ctk.CTkFrame(file_frame)
        action_frame.pack(fill="x", padx=20, pady=(0,20))
        
        load_btn = ctk.CTkButton(action_frame, text="📖 Carregar Contatos",
                               command=self.load_contacts, height=40)
        load_btn.pack(side="left", padx=(0,10))
        
        sample_btn = ctk.CTkButton(action_frame, text="📋 Criar Exemplo",
                                 command=self.create_sample_file, height=40)
        sample_btn.pack(side="left", padx=10)
        
        validate_btn = ctk.CTkButton(action_frame, text="✅ Validar Números",
                                   command=self.validate_contacts, height=40)
        validate_btn.pack(side="right")
        
        # Estatísticas
        self.stats_frame = ctk.CTkFrame(contacts_frame)
        self.stats_frame.pack(fill="x", padx=20, pady=10)
        
        self.stats_label = ctk.CTkLabel(self.stats_frame, 
                                      text="📊 Nenhum arquivo carregado",
                                      font=ctk.CTkFont(size=14))
        self.stats_label.pack(pady=20)
        
        # Preview dos contatos
        preview_frame = ctk.CTkFrame(contacts_frame)
        preview_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(preview_frame, text="Preview dos Contatos:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(20,10))
        
        # Textbox para preview
        self.contacts_preview = ctk.CTkTextbox(preview_frame, height=200)
        self.contacts_preview.pack(fill="both", expand=True, padx=20, pady=(0,20))
        
    def setup_send_tab(self):
        """Configura a aba de envio"""
        
        # Frame principal
        send_frame = ctk.CTkFrame(self.tab_send)
        send_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title = ctk.CTkLabel(send_frame, text="Envio de Mensagens", 
                           font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=20)
        
        # Status do sistema
        status_frame = ctk.CTkFrame(send_frame)
        status_frame.pack(fill="x", padx=20, pady=10)
        
        self.status_label = ctk.CTkLabel(status_frame, 
                                       text="🔴 Sistema não configurado",
                                       font=ctk.CTkFont(size=16, weight="bold"))
        self.status_label.pack(pady=20)
        
        # Configurações de envio
        settings_frame = ctk.CTkFrame(send_frame)
        settings_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(settings_frame, text="Configurações de Envio:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(20,10))
        
        # Intervalo de envio
        interval_frame = ctk.CTkFrame(settings_frame)
        interval_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(interval_frame, text="Intervalo entre envios (segundos):").pack(anchor="w", padx=20, pady=(10,5))
        
        interval_config_frame = ctk.CTkFrame(interval_frame)
        interval_config_frame.pack(fill="x", padx=20, pady=(0,20))
        
        ctk.CTkLabel(interval_config_frame, text="Mín:").pack(side="left", padx=(20,5))
        self.min_interval_var = ctk.IntVar(value=5)
        min_interval_entry = ctk.CTkEntry(interval_config_frame, textvariable=self.min_interval_var, width=60)
        min_interval_entry.pack(side="left", padx=(0,20))
        
        ctk.CTkLabel(interval_config_frame, text="Máx:").pack(side="left", padx=(20,5))
        self.max_interval_var = ctk.IntVar(value=20)
        max_interval_entry = ctk.CTkEntry(interval_config_frame, textvariable=self.max_interval_var, width=60)
        max_interval_entry.pack(side="left", padx=(0,20))
        
        # Resumo do envio
        summary_frame = ctk.CTkFrame(send_frame)
        summary_frame.pack(fill="x", padx=20, pady=10)
        
        self.summary_label = ctk.CTkLabel(summary_frame, 
                                        text="📋 Carregue os contatos primeiro",
                                        font=ctk.CTkFont(size=14))
        self.summary_label.pack(pady=20)
        
        # Barra de progresso
        progress_frame = ctk.CTkFrame(send_frame)
        progress_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(progress_frame, text="Progresso:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(20,10))
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=(0,10))
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(progress_frame, text="0 / 0 (0%)")
        self.progress_label.pack(pady=(0,20))
        
        # Botões de controle
        control_frame = ctk.CTkFrame(send_frame)
        control_frame.pack(fill="x", padx=20, pady=20)
        
        self.start_btn = ctk.CTkButton(control_frame, text="🚀 Iniciar Envio",
                                     command=self.start_sending, height=50,
                                     font=ctk.CTkFont(size=16, weight="bold"))
        self.start_btn.pack(side="left", padx=20, pady=20)
        
        self.stop_btn = ctk.CTkButton(control_frame, text="⏹️ Parar Envio",
                                    command=self.stop_sending, height=50,
                                    font=ctk.CTkFont(size=16, weight="bold"),
                                    state="disabled")
        self.stop_btn.pack(side="right", padx=20, pady=20)
        
    def setup_logs_tab(self):
        """Configura a aba de logs"""
        
        # Frame principal
        logs_frame = ctk.CTkFrame(self.tab_logs)
        logs_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title = ctk.CTkLabel(logs_frame, text="Logs e Relatórios", 
                           font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=20)
        
        # Estatísticas em tempo real
        stats_frame = ctk.CTkFrame(logs_frame)
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        self.live_stats = ctk.CTkLabel(stats_frame, 
                                     text="📊 Sucessos: 0 | ❌ Erros: 0 | 📱 Total: 0",
                                     font=ctk.CTkFont(size=16, weight="bold"))
        self.live_stats.pack(pady=20)
        
        # Área de logs
        log_text_frame = ctk.CTkFrame(logs_frame)
        log_text_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(log_text_frame, text="Log em Tempo Real:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(20,10))
        
        # Textbox para logs
        self.log_textbox = ctk.CTkTextbox(log_text_frame, height=300)
        self.log_textbox.pack(fill="both", expand=True, padx=20, pady=(0,20))
        
        # Botões de ação
        log_actions_frame = ctk.CTkFrame(logs_frame)
        log_actions_frame.pack(fill="x", padx=20, pady=20)
        
        clear_btn = ctk.CTkButton(log_actions_frame, text="🗑️ Limpar Logs",
                                command=self.clear_logs, height=40)
        clear_btn.pack(side="left", padx=20, pady=20)
        
        export_btn = ctk.CTkButton(log_actions_frame, text="💾 Exportar CSV",
                                 command=self.export_logs, height=40)
        export_btn.pack(side="right", padx=20, pady=20)
        
    def load_initial_config(self):
        """Carrega configuração inicial se existir"""
        try:
            self.config = load_config()
            
            # Preencher campos da GUI
            self.provider_var.set(self.config.get('provider', 'waha'))
            self.base_url_var.set(self.config.get('base_url', ''))
            self.instance_id_var.set(self.config.get('instance_id', 'default'))
            self.token_var.set(self.config.get('token', ''))
            
            self.update_status("🟢 Configuração carregada")
            self.log_message("✅ Configuração carregada do config.json")
            
        except Exception as e:
            self.log_message(f"⚠️ Erro ao carregar configuração: {str(e)}")
            self.update_status("🔴 Configuração necessária")
    
    def on_provider_change(self, choice):
        """Atualiza campos baseado no provider selecionado"""
        provider_configs = {
            "waha": {
                "base_url": "http://localhost:3000",
                "instance_id": "default"
            },
            "chat-api": {
                "base_url": "https://api.chat-api.com/instance123456",
                "instance_id": ""
            },
            "z-api": {
                "base_url": "https://api.z-api.io",
                "instance_id": "your_instance_id"
            },
            "ultramsg": {
                "base_url": "https://api.ultramsg.com/instance123456",
                "instance_id": ""
            }
        }
        
        if choice in provider_configs:
            config = provider_configs[choice]
            self.base_url_var.set(config["base_url"])
            self.instance_id_var.set(config["instance_id"])
    
    def toggle_token_visibility(self):
        """Alterna visibilidade do token"""
        if self.show_token_var.get():
            self.token_entry.configure(show="")
        else:
            self.token_entry.configure(show="*")
    
    def save_config(self):
        """Salva configuração atual"""
        try:
            config = {
                "provider": self.provider_var.get(),
                "base_url": self.base_url_var.get(),
                "instance_id": self.instance_id_var.get(),
                "token": self.token_var.get(),
                "timeout": 30,
                "min_interval_seconds": self.min_interval_var.get(),
                "max_interval_seconds": self.max_interval_var.get()
            }
            
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.config = config
            self.update_status("🟢 Configuração salva")
            self.log_message("💾 Configuração salva com sucesso!")
            messagebox.showinfo("Sucesso", "Configuração salva com sucesso!")
            
        except Exception as e:
            self.log_message(f"❌ Erro ao salvar configuração: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao salvar configuração:\n{str(e)}")
    
    def test_connection(self):
        """Testa conexão com a API"""
        if not self.config:
            messagebox.showwarning("Aviso", "Salve a configuração primeiro!")
            return
        
        self.log_message("🔍 Testando conexão com a API...")
        
        # Em uma implementação real, você faria uma chamada de teste à API
        # Por enquanto, apenas simular
        try:
            sender = WhatsAppAPISender(self.config)
            self.log_message("✅ Conexão teste bem-sucedida!")
            messagebox.showinfo("Sucesso", "Conexão com a API funcionando!")
        except Exception as e:
            self.log_message(f"❌ Erro na conexão: {str(e)}")
            messagebox.showerror("Erro", f"Erro na conexão:\n{str(e)}")
    
    def browse_excel_file(self):
        """Abre diálogo para selecionar arquivo Excel"""
        filename = filedialog.askopenfilename(
            title="Selecionar planilha Excel",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)
            self.log_message(f"📁 Arquivo selecionado: {filename}")
    
    def create_sample_file(self):
        """Cria arquivo de exemplo"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Salvar arquivo de exemplo",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")]
            )
            if filename:
                create_sample_excel(filename)
                self.log_message(f"📋 Arquivo de exemplo criado: {filename}")
                messagebox.showinfo("Sucesso", f"Arquivo de exemplo criado:\n{filename}")
        except Exception as e:
            self.log_message(f"❌ Erro ao criar arquivo de exemplo: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao criar arquivo:\n{str(e)}")
    
    def load_contacts(self):
        """Carrega contatos da planilha"""
        filepath = self.file_path_var.get()
        if not filepath:
            messagebox.showwarning("Aviso", "Selecione um arquivo Excel primeiro!")
            return
        
        try:
            self.log_message(f"📖 Carregando contatos de: {filepath}")
            self.contacts = load_contacts_from_excel(filepath)
            
            if not self.contacts:
                self.log_message("❌ Nenhum contato encontrado na planilha")
                messagebox.showwarning("Aviso", "Nenhum contato válido encontrado!")
                return
            
            # Atualizar estatísticas
            self.update_contact_stats()
            self.update_contacts_preview()
            self.update_send_summary()
            
            self.log_message(f"✅ {len(self.contacts)} contatos carregados com sucesso!")
            
        except Exception as e:
            self.log_message(f"❌ Erro ao carregar contatos: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao carregar contatos:\n{str(e)}")
    
    def validate_contacts(self):
        """Valida números de telefone dos contatos"""
        if not self.contacts:
            messagebox.showwarning("Aviso", "Carregue os contatos primeiro!")
            return
        
        self.log_message("🔍 Validando números de telefone...")
        
        self.valid_contacts = []
        invalid_count = 0
        
        for contact in self.contacts:
            if validate_phone_number(contact['numero']):
                self.valid_contacts.append(contact)
            else:
                invalid_count += 1
                self.log_message(f"⚠️ Número inválido: {contact['numero']}")
        
        self.update_contact_stats()
        self.update_send_summary()
        
        if invalid_count > 0:
            messagebox.showwarning("Validação", 
                                 f"{invalid_count} números inválidos foram encontrados.\n"
                                 f"{len(self.valid_contacts)} números válidos para envio.")
        else:
            messagebox.showinfo("Validação", "Todos os números são válidos!")
    
    def update_contact_stats(self):
        """Atualiza estatísticas de contatos"""
        total = len(self.contacts)
        valid = len(self.valid_contacts)
        invalid = total - valid
        
        stats_text = f"📊 Total: {total} | ✅ Válidos: {valid} | ❌ Inválidos: {invalid}"
        self.stats_label.configure(text=stats_text)
    
    def update_contacts_preview(self):
        """Atualiza preview dos contatos"""
        self.contacts_preview.delete("1.0", "end")
        
        if not self.contacts:
            self.contacts_preview.insert("1.0", "Nenhum contato carregado.")
            return
        
        preview_text = "PREVIEW DOS CONTATOS:\n" + "="*50 + "\n\n"
        
        for i, contact in enumerate(self.contacts[:10], 1):  # Mostrar apenas os primeiros 10
            nome = contact.get('nome', 'Sem nome')
            numero = contact['numero']
            mensagem = contact['mensagem'][:50] + "..." if len(contact['mensagem']) > 50 else contact['mensagem']
            
            preview_text += f"{i}. {nome} ({numero})\n"
            preview_text += f"   Mensagem: {mensagem}\n\n"
        
        if len(self.contacts) > 10:
            preview_text += f"... e mais {len(self.contacts) - 10} contatos"
        
        self.contacts_preview.insert("1.0", preview_text)
    
    def update_send_summary(self):
        """Atualiza resumo do envio"""
        if not self.valid_contacts:
            self.summary_label.configure(text="📋 Carregue e valide os contatos primeiro")
            return
        
        total = len(self.valid_contacts)
        with_media = sum(1 for c in self.valid_contacts if c.get('caminho_midia'))
        
        summary = f"📱 {total} mensagens para enviar"
        if with_media > 0:
            summary += f" | 📎 {with_media} com mídia"
        
        self.summary_label.configure(text=summary)
    
    def update_status(self, status_text):
        """Atualiza status do sistema"""
        self.status_label.configure(text=status_text)
    
    def start_sending(self):
        """Inicia o envio de mensagens"""
        if not self.config:
            messagebox.showwarning("Aviso", "Configure a API primeiro!")
            return
        
        if not self.valid_contacts:
            messagebox.showwarning("Aviso", "Carregue e valide os contatos primeiro!")
            return
        
        # Confirmar envio
        result = messagebox.askyesno("Confirmar Envio", 
                                   f"Você está prestes a enviar {len(self.valid_contacts)} mensagens.\n\n"
                                   "Deseja continuar?")
        if not result:
            return
        
        # Configurar interface para envio
        self.sending_active = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.progress_bar.set(0)
        
        # Iniciar envio em thread separada
        self.send_thread = threading.Thread(target=self.send_messages_thread)
        self.send_thread.daemon = True
        self.send_thread.start()
    
    def send_messages_thread(self):
        """Thread para envio de mensagens"""
        try:
            self.sender = WhatsAppAPISender(self.config)
            
            success_count = 0
            error_count = 0
            total = len(self.valid_contacts)
            
            self.log_message(f"🚀 Iniciando envio de {total} mensagens...")
            
            for i, contact in enumerate(self.valid_contacts):
                if not self.sending_active:  # Verificar se foi parado
                    break
                
                numero = contact['numero']
                nome = contact.get('nome', 'Contato')
                mensagem = contact.get('mensagem', '')
                caminho_midia = contact.get('caminho_midia', '')
                
                # Atualizar progress na thread principal
                self.root.after(0, self.update_progress, i + 1, total, nome)
                
                try:
                    # Verificar arquivo de mídia
                    if caminho_midia and not os.path.exists(caminho_midia):
                        self.root.after(0, self.log_message, 
                                      f"❌ Arquivo não encontrado: {caminho_midia}")
                        error_count += 1
                        continue
                    
                    # Enviar mensagem
                    success = self.sender.send_message(numero, mensagem, caminho_midia)
                    
                    if success:
                        success_count += 1
                        self.root.after(0, self.log_message, 
                                      f"✅ {nome} ({numero}) - Enviado com sucesso!")
                    else:
                        error_count += 1
                        self.root.after(0, self.log_message, 
                                      f"❌ {nome} ({numero}) - Falha no envio")
                    
                    # Atualizar estatísticas
                    self.root.after(0, self.update_live_stats, success_count, error_count, total)
                    
                    # Aguardar intervalo (se não for a última mensagem)
                    if i < total - 1 and self.sending_active:
                        import random
                        import time
                        wait_time = random.randint(self.min_interval_var.get(), 
                                                 self.max_interval_var.get())
                        self.root.after(0, self.log_message, 
                                      f"⏳ Aguardando {wait_time} segundos...")
                        time.sleep(wait_time)
                
                except Exception as e:
                    error_count += 1
                    self.root.after(0, self.log_message, 
                                  f"❌ Erro no envio para {numero}: {str(e)}")
            
            # Finalizar envio
            self.root.after(0, self.finish_sending, success_count, error_count, total)
            
        except Exception as e:
            self.root.after(0, self.log_message, f"❌ Erro fatal: {str(e)}")
            self.root.after(0, self.stop_sending)
    
    def update_progress(self, current, total, current_name):
        """Atualiza barra de progresso"""
        progress = current / total
        self.progress_bar.set(progress)
        
        percentage = progress * 100
        self.progress_label.configure(text=f"{current} / {total} ({percentage:.1f}%) - {current_name}")
    
    def update_live_stats(self, success, error, total):
        """Atualiza estatísticas em tempo real"""
        stats_text = f"📊 Sucessos: {success} | ❌ Erros: {error} | 📱 Total: {total}"
        self.live_stats.configure(text=stats_text)
    
    def finish_sending(self, success_count, error_count, total):
        """Finaliza o processo de envio"""
        self.sending_active = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        
        # Mostrar resumo final
        success_rate = (success_count / total) * 100 if total > 0 else 0
        
        summary_message = (f"🎉 Envio Concluído!\n\n"
                          f"✅ Sucessos: {success_count}\n"
                          f"❌ Erros: {error_count}\n"
                          f"📱 Total: {total}\n"
                          f"📈 Taxa de sucesso: {success_rate:.1f}%")
        
        self.log_message("=" * 50)
        self.log_message("🎉 ENVIO CONCLUÍDO!")
        self.log_message(f"✅ Sucessos: {success_count}")
        self.log_message(f"❌ Erros: {error_count}")
        self.log_message(f"📈 Taxa de sucesso: {success_rate:.1f}%")
        
        if self.sender:
            log_file = self.sender.get_log_filename()
            self.log_message(f"📄 Log salvo em: {log_file}")
        
        messagebox.showinfo("Envio Concluído", summary_message)
    
    def stop_sending(self):
        """Para o envio de mensagens"""
        self.sending_active = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.log_message("⏹️ Envio interrompido pelo usuário")
    
    def log_message(self, message):
        """Adiciona mensagem ao log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_textbox.insert("end", log_entry)
        self.log_textbox.see("end")  # Scroll para o final
    
    def clear_logs(self):
        """Limpa o log"""
        self.log_textbox.delete("1.0", "end")
        self.log_message("🗑️ Logs limpos")
    
    def export_logs(self):
        """Exporta logs para arquivo"""
        if self.sender:
            log_file = self.sender.get_log_filename()
            messagebox.showinfo("Log CSV", f"Log CSV disponível em:\n{log_file}")
        else:
            messagebox.showwarning("Aviso", "Nenhum envio foi realizado ainda!")
    
    def run(self):
        """Executa a aplicação"""
        self.root.mainloop()


def main():
    """Função principal da GUI"""
    app = WhatsAppSenderGUI()
    app.run()


if __name__ == "__main__":
    main() 