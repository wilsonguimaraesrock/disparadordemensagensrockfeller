#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instalador Automático do Sistema de Solução de Mídia WAHA

Este script configura automaticamente todo o sistema de diagnóstico,
teste e monitoramento de mídia para o WAHA.

Uso:
    python instalar_sistema_midia.py
    python instalar_sistema_midia.py --config-apenas
    python instalar_sistema_midia.py --verificar

Autor: Sistema de Automação WAHA
Data: Janeiro 2024
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

class InstaladorSistemaMidia:
    def __init__(self):
        self.base_dir = Path.cwd()
        self.config_file = self.base_dir / "config.json"
        self.scripts_necessarios = [
            "solucionar_midia_waha.py",
            "diagnostico_midia_waha.py",
            "teste_formatos_midia.py",
            "monitor_waha_realtime.py"
        ]
        self.arquivos_documentacao = [
            "GUIA_SOLUCAO_MIDIA_WAHA.md",
            "README_SOLUCAO_MIDIA.md"
        ]
        
    def print_banner(self):
        """Exibe banner de boas-vindas"""
        print("\n" + "="*70)
        print("🔧 INSTALADOR DO SISTEMA DE SOLUÇÃO DE MÍDIA WAHA")
        print("="*70)
        print("📋 Configuração automática de diagnóstico e monitoramento")
        print("🎯 Resolução automática de problemas de envio de mídia")
        print("📊 Monitoramento em tempo real do WAHA")
        print("="*70 + "\n")
        
    def verificar_python(self):
        """Verifica versão do Python"""
        print("🐍 Verificando versão do Python...")
        
        if sys.version_info < (3, 7):
            print("❌ Python 3.7+ é necessário")
            print(f"   Versão atual: {sys.version}")
            return False
            
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
        return True
        
    def verificar_dependencias(self):
        """Verifica e instala dependências"""
        print("\n📦 Verificando dependências...")
        
        dependencias = ['requests']
        faltando = []
        
        for dep in dependencias:
            try:
                __import__(dep)
                print(f"✅ {dep} - OK")
            except ImportError:
                print(f"❌ {dep} - FALTANDO")
                faltando.append(dep)
                
        if faltando:
            print(f"\n📥 Instalando dependências faltando: {', '.join(faltando)}")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + faltando)
                print("✅ Dependências instaladas com sucesso")
                return True
            except subprocess.CalledProcessError:
                print("❌ Erro ao instalar dependências")
                print("   Execute manualmente: pip install requests")
                return False
        
        print("✅ Todas as dependências estão instaladas")
        return True
        
    def verificar_scripts(self):
        """Verifica se todos os scripts estão presentes"""
        print("\n📄 Verificando scripts do sistema...")
        
        scripts_faltando = []
        
        for script in self.scripts_necessarios:
            script_path = self.base_dir / script
            if script_path.exists():
                print(f"✅ {script} - OK")
            else:
                print(f"❌ {script} - FALTANDO")
                scripts_faltando.append(script)
                
        if scripts_faltando:
            print(f"\n⚠️  Scripts faltando: {', '.join(scripts_faltando)}")
            print("   Certifique-se de que todos os arquivos foram criados")
            return False
            
        print("✅ Todos os scripts estão presentes")
        return True
        
    def criar_configuracao(self):
        """Cria arquivo de configuração inicial"""
        print("\n⚙️  Criando configuração inicial...")
        
        if self.config_file.exists():
            print("📋 Arquivo config.json já existe")
            
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print("✅ Configuração carregada com sucesso")
                return True
            except Exception as e:
                print(f"⚠️  Erro ao ler configuração existente: {e}")
                print("   Criando nova configuração...")
        
        # Solicitar configurações do usuário
        print("\n📝 Configure seu WAHA:")
        
        base_url = input("🌐 URL do WAHA [http://localhost:3000]: ").strip()
        if not base_url:
            base_url = "http://localhost:3000"
            
        token = input("🔑 Token de API do WAHA: ").strip()
        if not token:
            print("⚠️  Token não fornecido - você pode configurar depois")
            token = "seu-token-aqui"
            
        instance_id = input("📱 ID da Instância [default]: ").strip()
        if not instance_id:
            instance_id = "default"
            
        config = {
            "base_url": base_url,
            "token": token,
            "instance_id": instance_id,
            "provider": "waha",
            "timeout": 60,
            "max_retries": 3,
            "created_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"✅ Configuração salva em {self.config_file}")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar configuração: {e}")
            return False
            
    def criar_diretorio_logs(self):
        """Cria diretório para logs"""
        print("\n📁 Criando diretório de logs...")
        
        logs_dir = self.base_dir / "logs"
        
        try:
            logs_dir.mkdir(exist_ok=True)
            print(f"✅ Diretório de logs: {logs_dir}")
            
            # Criar arquivo .gitignore para logs
            gitignore_path = logs_dir / ".gitignore"
            with open(gitignore_path, 'w') as f:
                f.write("# Logs do sistema\n*.log\n*.json\n")
                
            return True
        except Exception as e:
            print(f"❌ Erro ao criar diretório de logs: {e}")
            return False
            
    def criar_diretorio_teste(self):
        """Cria diretório para arquivos de teste"""
        print("\n🧪 Criando diretório de teste...")
        
        teste_dir = self.base_dir / "arquivos_teste"
        
        try:
            teste_dir.mkdir(exist_ok=True)
            print(f"✅ Diretório de teste: {teste_dir}")
            
            # Criar arquivo README no diretório de teste
            readme_path = teste_dir / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write("# Arquivos de Teste\n\n")
                f.write("Este diretório contém arquivos para testar o envio de mídia.\n\n")
                f.write("## Formatos Suportados\n\n")
                f.write("- **Imagens:** JPG, PNG, WebP (até 16MB)\n")
                f.write("- **Vídeos:** MP4, 3GP (até 16MB)\n")
                f.write("- **Áudios:** AAC, MP3, AMR, OGG (até 16MB)\n")
                f.write("- **Documentos:** PDF, DOC, XLS, TXT, ZIP (até 100MB)\n")
                
            return True
        except Exception as e:
            print(f"❌ Erro ao criar diretório de teste: {e}")
            return False
            
    def testar_instalacao(self):
        """Testa se a instalação foi bem-sucedida"""
        print("\n🧪 Testando instalação...")
        
        # Testar importação dos módulos
        try:
            sys.path.insert(0, str(self.base_dir))
            
            # Testar script principal
            print("📋 Testando script principal...")
            result = subprocess.run(
                [sys.executable, "solucionar_midia_waha.py", "--help"],
                capture_output=True,
                text=True,
                cwd=self.base_dir
            )
            
            if result.returncode == 0:
                print("✅ Script principal - OK")
            else:
                print(f"❌ Script principal - ERRO: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
            return False
            
        print("✅ Instalação testada com sucesso")
        return True
        
    def mostrar_proximos_passos(self):
        """Mostra os próximos passos após instalação"""
        print("\n" + "="*70)
        print("🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*70)
        
        print("\n📋 PRÓXIMOS PASSOS:")
        print("\n1. 🔧 Configure seu token WAHA (se ainda não fez):")
        print("   python solucionar_midia_waha.py --config")
        
        print("\n2. 🩺 Execute o diagnóstico inicial:")
        print("   python solucionar_midia_waha.py --diagnostico")
        
        print("\n3. 🎯 Use o menu interativo:")
        print("   python solucionar_midia_waha.py")
        
        print("\n4. 📊 Inicie o monitoramento:")
        print("   python monitor_waha_realtime.py")
        
        print("\n5. 🧪 Teste um arquivo:")
        print("   python teste_formatos_midia.py arquivo.jpg +5511999999999")
        
        print("\n📚 DOCUMENTAÇÃO:")
        print("   📖 README_SOLUCAO_MIDIA.md - Guia completo")
        print("   📖 GUIA_SOLUCAO_MIDIA_WAHA.md - Soluções detalhadas")
        
        print("\n🆘 SUPORTE:")
        print("   🔍 python solucionar_midia_waha.py --help")
        print("   🩺 python diagnostico_midia_waha.py")
        
        print("\n" + "="*70)
        print("✨ Sistema pronto para resolver problemas de mídia!")
        print("="*70 + "\n")
        
    def verificar_sistema_completo(self):
        """Verifica se o sistema está completamente instalado"""
        print("\n🔍 Verificando sistema completo...")
        
        verificacoes = {
            "Python 3.7+": self.verificar_python(),
            "Dependências": True,  # Será verificado separadamente
            "Scripts": self.verificar_scripts(),
            "Configuração": self.config_file.exists(),
            "Diretório logs": (self.base_dir / "logs").exists(),
            "Diretório teste": (self.base_dir / "arquivos_teste").exists()
        }
        
        # Verificar dependências separadamente
        try:
            import requests
            verificacoes["Dependências"] = True
        except ImportError:
            verificacoes["Dependências"] = False
            
        print("\n📊 RELATÓRIO DE VERIFICAÇÃO:")
        print("-" * 40)
        
        tudo_ok = True
        for item, status in verificacoes.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {item}")
            if not status:
                tudo_ok = False
                
        print("-" * 40)
        
        if tudo_ok:
            print("🎉 Sistema completamente instalado e funcional!")
        else:
            print("⚠️  Alguns componentes precisam de atenção")
            
        return tudo_ok
        
    def instalar_completo(self):
        """Executa instalação completa"""
        self.print_banner()
        
        etapas = [
            ("Verificar Python", self.verificar_python),
            ("Verificar dependências", self.verificar_dependencias),
            ("Verificar scripts", self.verificar_scripts),
            ("Criar configuração", self.criar_configuracao),
            ("Criar diretório de logs", self.criar_diretorio_logs),
            ("Criar diretório de teste", self.criar_diretorio_teste),
            ("Testar instalação", self.testar_instalacao)
        ]
        
        print(f"🚀 Iniciando instalação em {self.base_dir}")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        for nome, funcao in etapas:
            print(f"\n⏳ {nome}...")
            if not funcao():
                print(f"\n❌ FALHA na etapa: {nome}")
                print("🛑 Instalação interrompida")
                return False
                
        self.mostrar_proximos_passos()
        return True

def main():
    parser = argparse.ArgumentParser(
        description="Instalador do Sistema de Solução de Mídia WAHA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python instalar_sistema_midia.py              # Instalação completa
  python instalar_sistema_midia.py --verificar  # Apenas verificar sistema
  python instalar_sistema_midia.py --config     # Apenas configurar
        """
    )
    
    parser.add_argument(
        '--verificar',
        action='store_true',
        help='Apenas verificar se o sistema está instalado'
    )
    
    parser.add_argument(
        '--config',
        action='store_true',
        help='Apenas criar/atualizar configuração'
    )
    
    args = parser.parse_args()
    
    instalador = InstaladorSistemaMidia()
    
    if args.verificar:
        instalador.print_banner()
        instalador.verificar_sistema_completo()
    elif args.config:
        instalador.print_banner()
        instalador.criar_configuracao()
    else:
        # Instalação completa
        sucesso = instalador.instalar_completo()
        sys.exit(0 if sucesso else 1)

if __name__ == "__main__":
    main()