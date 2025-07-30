#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atualizador Automático do Sistema de Solução de Mídia WAHA

Este script mantém o sistema atualizado com as últimas correções
e melhorias para diagnóstico e resolução de problemas de mídia.

Uso:
    python atualizar_sistema_midia.py
    python atualizar_sistema_midia.py --verificar
    python atualizar_sistema_midia.py --backup
    python atualizar_sistema_midia.py --restaurar

Autor: Sistema de Automação WAHA
Data: Janeiro 2024
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime

class AtualizadorSistemaMidia:
    def __init__(self):
        self.base_dir = Path.cwd()
        self.backup_dir = self.base_dir / "backup_sistema"
        self.config_file = self.base_dir / "config.json"
        
        self.versao_atual = "1.0.0"
        self.versao_sistema = self.obter_versao_sistema()
        
        self.arquivos_sistema = [
            "solucionar_midia_waha.py",
            "diagnostico_midia_waha.py",
            "teste_formatos_midia.py",
            "monitor_waha_realtime.py",
            "instalar_sistema_midia.py",
            "atualizar_sistema_midia.py"
        ]
        
        self.arquivos_config = [
            "config.json",
            "env.example"
        ]
        
        self.arquivos_docs = [
            "GUIA_SOLUCAO_MIDIA_WAHA.md",
            "README_SOLUCAO_MIDIA.md",
            "LIMITACOES_WAHA_CORE.md"
        ]
        
    def print_banner(self):
        """Exibe banner do atualizador"""
        print("\n" + "="*70)
        print("🔄 ATUALIZADOR DO SISTEMA DE SOLUÇÃO DE MÍDIA WAHA")
        print("="*70)
        print(f"📦 Versão atual: {self.versao_atual}")
        print(f"💾 Versão instalada: {self.versao_sistema}")
        print("🔧 Manutenção automática de scripts e configurações")
        print("="*70 + "\n")
        
    def obter_versao_sistema(self):
        """Obtém versão atual do sistema"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('version', '0.0.0')
        except Exception:
            pass
        return "0.0.0"
        
    def verificar_atualizacoes_necessarias(self):
        """Verifica se há atualizações necessárias"""
        print("🔍 Verificando necessidade de atualizações...")
        
        atualizacoes = []
        
        # Verificar versão
        if self.versao_sistema < self.versao_atual:
            atualizacoes.append(f"Versão: {self.versao_sistema} → {self.versao_atual}")
            
        # Verificar arquivos faltando
        for arquivo in self.arquivos_sistema:
            if not (self.base_dir / arquivo).exists():
                atualizacoes.append(f"Arquivo faltando: {arquivo}")
                
        # Verificar configuração
        if not self.config_file.exists():
            atualizacoes.append("Configuração faltando")
            
        # Verificar diretórios
        dirs_necessarios = ["logs", "arquivos_teste"]
        for dir_name in dirs_necessarios:
            if not (self.base_dir / dir_name).exists():
                atualizacoes.append(f"Diretório faltando: {dir_name}")
                
        return atualizacoes
        
    def criar_backup(self):
        """Cria backup do sistema atual"""
        print("💾 Criando backup do sistema atual...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        
        try:
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Backup dos scripts
            scripts_backup = backup_path / "scripts"
            scripts_backup.mkdir(exist_ok=True)
            
            for arquivo in self.arquivos_sistema:
                arquivo_path = self.base_dir / arquivo
                if arquivo_path.exists():
                    shutil.copy2(arquivo_path, scripts_backup)
                    
            # Backup da configuração
            config_backup = backup_path / "config"
            config_backup.mkdir(exist_ok=True)
            
            for arquivo in self.arquivos_config:
                arquivo_path = self.base_dir / arquivo
                if arquivo_path.exists():
                    shutil.copy2(arquivo_path, config_backup)
                    
            # Backup dos logs (últimos 7 dias)
            logs_dir = self.base_dir / "logs"
            if logs_dir.exists():
                logs_backup = backup_path / "logs"
                logs_backup.mkdir(exist_ok=True)
                
                for log_file in logs_dir.glob("*.log"):
                    if (datetime.now() - datetime.fromtimestamp(log_file.stat().st_mtime)).days <= 7:
                        shutil.copy2(log_file, logs_backup)
                        
            # Criar manifesto do backup
            manifesto = {
                "timestamp": timestamp,
                "versao_sistema": self.versao_sistema,
                "arquivos_backup": {
                    "scripts": [f.name for f in scripts_backup.glob("*")],
                    "config": [f.name for f in config_backup.glob("*")],
                    "logs": [f.name for f in (logs_backup.glob("*") if logs_backup.exists() else [])]
                }
            }
            
            with open(backup_path / "manifesto.json", 'w', encoding='utf-8') as f:
                json.dump(manifesto, f, indent=2, ensure_ascii=False)
                
            print(f"✅ Backup criado em: {backup_path}")
            return backup_path
            
        except Exception as e:
            print(f"❌ Erro ao criar backup: {e}")
            return None
            
    def listar_backups(self):
        """Lista backups disponíveis"""
        if not self.backup_dir.exists():
            return []
            
        backups = []
        for backup_path in self.backup_dir.glob("backup_*"):
            if backup_path.is_dir():
                manifesto_path = backup_path / "manifesto.json"
                if manifesto_path.exists():
                    try:
                        with open(manifesto_path, 'r', encoding='utf-8') as f:
                            manifesto = json.load(f)
                        backups.append({
                            "path": backup_path,
                            "timestamp": manifesto["timestamp"],
                            "versao": manifesto.get("versao_sistema", "desconhecida")
                        })
                    except Exception:
                        pass
                        
        return sorted(backups, key=lambda x: x["timestamp"], reverse=True)
        
    def restaurar_backup(self, backup_path=None):
        """Restaura backup específico"""
        if backup_path is None:
            backups = self.listar_backups()
            if not backups:
                print("❌ Nenhum backup encontrado")
                return False
                
            print("📋 Backups disponíveis:")
            for i, backup in enumerate(backups):
                print(f"  {i+1}. {backup['timestamp']} (v{backup['versao']})")
                
            try:
                escolha = int(input("\nEscolha o backup (número): ")) - 1
                if 0 <= escolha < len(backups):
                    backup_path = backups[escolha]["path"]
                else:
                    print("❌ Escolha inválida")
                    return False
            except ValueError:
                print("❌ Entrada inválida")
                return False
                
        print(f"🔄 Restaurando backup de {backup_path.name}...")
        
        try:
            # Restaurar scripts
            scripts_backup = backup_path / "scripts"
            if scripts_backup.exists():
                for script_file in scripts_backup.glob("*"):
                    shutil.copy2(script_file, self.base_dir)
                    print(f"✅ Restaurado: {script_file.name}")
                    
            # Restaurar configuração (com confirmação)
            config_backup = backup_path / "config"
            if config_backup.exists():
                for config_file in config_backup.glob("*"):
                    destino = self.base_dir / config_file.name
                    if destino.exists():
                        resposta = input(f"⚠️  Sobrescrever {config_file.name}? (s/N): ")
                        if resposta.lower() != 's':
                            continue
                    shutil.copy2(config_file, self.base_dir)
                    print(f"✅ Restaurado: {config_file.name}")
                    
            print("✅ Backup restaurado com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao restaurar backup: {e}")
            return False
            
    def atualizar_configuracao(self):
        """Atualiza arquivo de configuração"""
        print("⚙️  Atualizando configuração...")
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}
                
            # Atualizar versão
            config["version"] = self.versao_atual
            config["updated_at"] = datetime.now().isoformat()
            
            # Adicionar novos campos se não existirem
            defaults = {
                "base_url": "http://localhost:3000",
                "token": "seu-token-aqui",
                "instance_id": "default",
                "provider": "waha",
                "timeout": 60,
                "max_retries": 3,
                "debug": False,
                "log_level": "INFO"
            }
            
            for key, value in defaults.items():
                if key not in config:
                    config[key] = value
                    
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
            print("✅ Configuração atualizada")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao atualizar configuração: {e}")
            return False
            
    def verificar_integridade_arquivos(self):
        """Verifica integridade dos arquivos do sistema"""
        print("🔍 Verificando integridade dos arquivos...")
        
        problemas = []
        
        for arquivo in self.arquivos_sistema:
            arquivo_path = self.base_dir / arquivo
            
            if not arquivo_path.exists():
                problemas.append(f"Arquivo faltando: {arquivo}")
                continue
                
            # Verificar se o arquivo é executável (para scripts Python)
            if arquivo.endswith('.py'):
                try:
                    with open(arquivo_path, 'r', encoding='utf-8') as f:
                        conteudo = f.read()
                        
                    # Verificações básicas
                    if len(conteudo) < 100:
                        problemas.append(f"Arquivo muito pequeno: {arquivo}")
                    elif not conteudo.startswith(('#!', '# -*-')):
                        problemas.append(f"Cabeçalho faltando: {arquivo}")
                        
                except Exception as e:
                    problemas.append(f"Erro ao ler {arquivo}: {e}")
                    
        if problemas:
            print("⚠️  Problemas encontrados:")
            for problema in problemas:
                print(f"   - {problema}")
            return False
        else:
            print("✅ Todos os arquivos estão íntegros")
            return True
            
    def limpar_arquivos_antigos(self):
        """Remove arquivos antigos e temporários"""
        print("🧹 Limpando arquivos antigos...")
        
        removidos = 0
        
        # Limpar logs antigos (mais de 30 dias)
        logs_dir = self.base_dir / "logs"
        if logs_dir.exists():
            for log_file in logs_dir.glob("*.log"):
                if (datetime.now() - datetime.fromtimestamp(log_file.stat().st_mtime)).days > 30:
                    log_file.unlink()
                    removidos += 1
                    
        # Limpar relatórios antigos (mais de 14 dias)
        for relatorio in self.base_dir.glob("*relatorio_*.json"):
            if (datetime.now() - datetime.fromtimestamp(relatorio.stat().st_mtime)).days > 14:
                relatorio.unlink()
                removidos += 1
                
        # Limpar backups antigos (mais de 90 dias)
        if self.backup_dir.exists():
            for backup in self.backup_dir.glob("backup_*"):
                if backup.is_dir():
                    if (datetime.now() - datetime.fromtimestamp(backup.stat().st_mtime)).days > 90:
                        shutil.rmtree(backup)
                        removidos += 1
                        
        print(f"✅ {removidos} arquivos antigos removidos")
        return removidos
        
    def executar_atualizacao_completa(self):
        """Executa atualização completa do sistema"""
        self.print_banner()
        
        print(f"🚀 Iniciando atualização em {self.base_dir}")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Verificar se há atualizações necessárias
        atualizacoes = self.verificar_atualizacoes_necessarias()
        
        if not atualizacoes:
            print("\n✅ Sistema já está atualizado!")
            print("🔍 Executando verificação de integridade...")
            self.verificar_integridade_arquivos()
            self.limpar_arquivos_antigos()
            return True
            
        print("\n📋 Atualizações necessárias:")
        for atualizacao in atualizacoes:
            print(f"   - {atualizacao}")
            
        resposta = input("\n🔄 Continuar com a atualização? (S/n): ")
        if resposta.lower() == 'n':
            print("❌ Atualização cancelada")
            return False
            
        # Criar backup antes da atualização
        backup_path = self.criar_backup()
        if not backup_path:
            print("❌ Falha ao criar backup - atualização cancelada")
            return False
            
        try:
            # Executar atualizações
            print("\n🔄 Executando atualizações...")
            
            # Atualizar configuração
            if not self.atualizar_configuracao():
                raise Exception("Falha ao atualizar configuração")
                
            # Criar diretórios se necessário
            for dir_name in ["logs", "arquivos_teste"]:
                dir_path = self.base_dir / dir_name
                if not dir_path.exists():
                    dir_path.mkdir(exist_ok=True)
                    print(f"✅ Diretório criado: {dir_name}")
                    
            # Verificar integridade
            if not self.verificar_integridade_arquivos():
                print("⚠️  Alguns arquivos podem precisar de atenção")
                
            # Limpeza
            self.limpar_arquivos_antigos()
            
            print("\n🎉 Atualização concluída com sucesso!")
            print(f"📦 Sistema atualizado para versão {self.versao_atual}")
            print(f"💾 Backup salvo em: {backup_path}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Erro durante atualização: {e}")
            print(f"🔄 Restaurando backup de {backup_path}...")
            
            if self.restaurar_backup(backup_path):
                print("✅ Sistema restaurado com sucesso")
            else:
                print("❌ Falha ao restaurar backup")
                
            return False
            
    def mostrar_status_sistema(self):
        """Mostra status detalhado do sistema"""
        self.print_banner()
        
        print("📊 STATUS DO SISTEMA:")
        print("-" * 50)
        
        # Verificar arquivos
        print("\n📄 Arquivos do Sistema:")
        for arquivo in self.arquivos_sistema:
            arquivo_path = self.base_dir / arquivo
            if arquivo_path.exists():
                tamanho = arquivo_path.stat().st_size
                modificado = datetime.fromtimestamp(arquivo_path.stat().st_mtime)
                print(f"   ✅ {arquivo} ({tamanho:,} bytes, {modificado.strftime('%Y-%m-%d %H:%M')})")
            else:
                print(f"   ❌ {arquivo} - FALTANDO")
                
        # Verificar configuração
        print("\n⚙️  Configuração:")
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"   ✅ config.json (versão {config.get('version', 'desconhecida')})")
                print(f"   🌐 URL: {config.get('base_url', 'não configurada')}")
                print(f"   🔑 Token: {'configurado' if config.get('token') != 'seu-token-aqui' else 'não configurado'}")
            except Exception as e:
                print(f"   ❌ Erro ao ler configuração: {e}")
        else:
            print("   ❌ config.json - FALTANDO")
            
        # Verificar diretórios
        print("\n📁 Diretórios:")
        for dir_name in ["logs", "arquivos_teste", "backup_sistema"]:
            dir_path = self.base_dir / dir_name
            if dir_path.exists():
                arquivos = len(list(dir_path.glob("*")))
                print(f"   ✅ {dir_name}/ ({arquivos} arquivos)")
            else:
                print(f"   ❌ {dir_name}/ - FALTANDO")
                
        # Verificar backups
        backups = self.listar_backups()
        print(f"\n💾 Backups: {len(backups)} disponíveis")
        if backups:
            backup_mais_recente = backups[0]
            print(f"   📅 Mais recente: {backup_mais_recente['timestamp']} (v{backup_mais_recente['versao']})")
            
        # Verificar atualizações
        atualizacoes = self.verificar_atualizacoes_necessarias()
        if atualizacoes:
            print(f"\n🔄 Atualizações disponíveis: {len(atualizacoes)}")
            for atualizacao in atualizacoes[:3]:  # Mostrar apenas as 3 primeiras
                print(f"   - {atualizacao}")
        else:
            print("\n✅ Sistema atualizado")
            
        print("-" * 50)

def main():
    parser = argparse.ArgumentParser(
        description="Atualizador do Sistema de Solução de Mídia WAHA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python atualizar_sistema_midia.py              # Atualização completa
  python atualizar_sistema_midia.py --verificar  # Verificar status
  python atualizar_sistema_midia.py --backup     # Criar backup
  python atualizar_sistema_midia.py --restaurar  # Restaurar backup
        """
    )
    
    parser.add_argument(
        '--verificar',
        action='store_true',
        help='Verificar status do sistema sem atualizar'
    )
    
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Criar backup do sistema atual'
    )
    
    parser.add_argument(
        '--restaurar',
        action='store_true',
        help='Restaurar backup anterior'
    )
    
    parser.add_argument(
        '--limpar',
        action='store_true',
        help='Limpar arquivos antigos'
    )
    
    args = parser.parse_args()
    
    atualizador = AtualizadorSistemaMidia()
    
    if args.verificar:
        atualizador.mostrar_status_sistema()
    elif args.backup:
        atualizador.print_banner()
        backup_path = atualizador.criar_backup()
        if backup_path:
            print(f"✅ Backup criado com sucesso em {backup_path}")
        else:
            print("❌ Falha ao criar backup")
            sys.exit(1)
    elif args.restaurar:
        atualizador.print_banner()
        if atualizador.restaurar_backup():
            print("✅ Backup restaurado com sucesso")
        else:
            print("❌ Falha ao restaurar backup")
            sys.exit(1)
    elif args.limpar:
        atualizador.print_banner()
        removidos = atualizador.limpar_arquivos_antigos()
        print(f"✅ Limpeza concluída - {removidos} arquivos removidos")
    else:
        # Atualização completa
        sucesso = atualizador.executar_atualizacao_completa()
        sys.exit(0 if sucesso else 1)

if __name__ == "__main__":
    main()