#!/usr/bin/env python3
"""
Solucionador Integrado de Problemas de Mídia no WAHA
Script principal que integra diagnóstico, teste e correção automática
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

class SolucionadorMidiaWAHA:
    def __init__(self):
        self.config_path = "config.json"
        self.scripts_disponiveis = {
            'diagnostico': 'diagnostico_midia_waha.py',
            'teste_formatos': 'teste_formatos_midia.py',
            'monitor': 'monitor_waha_realtime.py'
        }
        
        # Verificar se scripts existem
        self._verificar_scripts()
    
    def _verificar_scripts(self) -> None:
        """Verifica se todos os scripts necessários existem"""
        scripts_faltando = []
        
        for nome, arquivo in self.scripts_disponiveis.items():
            if not os.path.exists(arquivo):
                scripts_faltando.append(arquivo)
        
        if scripts_faltando:
            print("❌ Scripts necessários não encontrados:")
            for script in scripts_faltando:
                print(f"   • {script}")
            print("\n💡 Execute este script no diretório correto com todos os arquivos")
            sys.exit(1)
    
    def _executar_script(self, script: str, argumentos: List[str] = None) -> int:
        """Executa um script Python"""
        cmd = [sys.executable, script]
        if argumentos:
            cmd.extend(argumentos)
        
        try:
            return subprocess.call(cmd)
        except Exception as e:
            print(f"❌ Erro ao executar {script}: {e}")
            return 1
    
    def verificar_configuracao(self) -> bool:
        """Verifica se a configuração está correta"""
        print("🔍 Verificando configuração...")
        
        if not os.path.exists(self.config_path):
            print(f"❌ Arquivo {self.config_path} não encontrado")
            return self._criar_configuracao_interativa()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            campos_obrigatorios = ['base_url', 'token', 'instance_id', 'provider']
            campos_faltando = [campo for campo in campos_obrigatorios if not config.get(campo)]
            
            if campos_faltando:
                print(f"❌ Campos obrigatórios faltando: {', '.join(campos_faltando)}")
                return self._corrigir_configuracao(config, campos_faltando)
            
            if config.get('provider', '').lower() != 'waha':
                print("⚠️ Provider não está configurado como 'waha'")
                config['provider'] = 'waha'
                self._salvar_configuracao(config)
            
            print("✅ Configuração válida")
            return True
            
        except json.JSONDecodeError:
            print("❌ Arquivo de configuração com formato inválido")
            return self._criar_configuracao_interativa()
    
    def _criar_configuracao_interativa(self) -> bool:
        """Cria configuração interativamente"""
        print("\n🔧 Criando configuração do WAHA...")
        
        config = {}
        
        # URL base
        config['base_url'] = input("URL do WAHA [http://localhost:3000]: ").strip() or "http://localhost:3000"
        
        # Token
        token = input("Token de API do WAHA: ").strip()
        if not token:
            print("❌ Token é obrigatório")
            return False
        config['token'] = token
        
        # Instance ID
        config['instance_id'] = input("Instance ID [default]: ").strip() or "default"
        
        # Provider
        config['provider'] = 'waha'
        
        # Configurações adicionais
        config['timeout'] = 60
        config['max_retries'] = 3
        
        return self._salvar_configuracao(config)
    
    def _corrigir_configuracao(self, config: Dict, campos_faltando: List[str]) -> bool:
        """Corrige configuração existente"""
        print("\n🔧 Corrigindo configuração...")
        
        for campo in campos_faltando:
            if campo == 'base_url':
                config[campo] = input("URL do WAHA [http://localhost:3000]: ").strip() or "http://localhost:3000"
            elif campo == 'token':
                token = input("Token de API do WAHA: ").strip()
                if not token:
                    print("❌ Token é obrigatório")
                    return False
                config[campo] = token
            elif campo == 'instance_id':
                config[campo] = input("Instance ID [default]: ").strip() or "default"
            elif campo == 'provider':
                config[campo] = 'waha'
        
        return self._salvar_configuracao(config)
    
    def _salvar_configuracao(self, config: Dict) -> bool:
        """Salva configuração no arquivo"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"✅ Configuração salva em {self.config_path}")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar configuração: {e}")
            return False
    
    def executar_diagnostico_completo(self) -> bool:
        """Executa diagnóstico completo"""
        print("\n🔍 Executando diagnóstico completo...")
        print("=" * 50)
        
        resultado = self._executar_script(self.scripts_disponiveis['diagnostico'])
        return resultado == 0
    
    def testar_formatos_midia(self, arquivo: str = None, numero: str = None) -> bool:
        """Testa formatos de mídia"""
        print("\n🧪 Testando formatos de mídia...")
        print("=" * 40)
        
        args = []
        
        if not arquivo:
            # Listar formatos suportados
            args = ['--formatos']
        else:
            args = [arquivo]
            if numero:
                args.append(numero)
        
        resultado = self._executar_script(self.scripts_disponiveis['teste_formatos'], args)
        return resultado == 0
    
    def iniciar_monitoramento(self, intervalo: int = 30) -> None:
        """Inicia monitoramento em tempo real"""
        print(f"\n🔍 Iniciando monitoramento (intervalo: {intervalo}s)...")
        print("=" * 50)
        
        args = ['--intervalo', str(intervalo)] if intervalo != 30 else []
        self._executar_script(self.scripts_disponiveis['monitor'], args)
    
    def verificar_status_rapido(self) -> bool:
        """Verificação rápida de status"""
        print("\n⚡ Verificação rápida de status...")
        
        resultado = self._executar_script(self.scripts_disponiveis['monitor'], ['--status'])
        return resultado == 0
    
    def resolver_problemas_automaticamente(self) -> None:
        """Resolve problemas automaticamente seguindo um fluxo"""
        print("\n🔧 RESOLUÇÃO AUTOMÁTICA DE PROBLEMAS")
        print("=" * 50)
        
        # 1. Verificar configuração
        print("\n1️⃣ Verificando configuração...")
        if not self.verificar_configuracao():
            print("❌ Falha na configuração. Corrija antes de continuar.")
            return
        
        # 2. Executar diagnóstico
        print("\n2️⃣ Executando diagnóstico...")
        if not self.executar_diagnostico_completo():
            print("⚠️ Problemas detectados no diagnóstico")
        
        # 3. Verificar formatos
        print("\n3️⃣ Verificando formatos suportados...")
        self.testar_formatos_midia()
        
        # 4. Sugestões finais
        print("\n4️⃣ Sugestões finais...")
        self._mostrar_sugestoes_finais()
    
    def _mostrar_sugestoes_finais(self) -> None:
        """Mostra sugestões finais para resolução"""
        print("\n💡 SUGESTÕES PARA RESOLUÇÃO DE PROBLEMAS:")
        print("-" * 45)
        
        sugestoes = [
            "1. Verificar se o WAHA está rodando: docker ps",
            "2. Verificar logs do WAHA: docker logs container_waha",
            "3. Reiniciar WAHA se necessário: docker-compose restart",
            "4. Usar WAHA Plus para suporte completo a mídia",
            "5. Verificar se a sessão WhatsApp está conectada",
            "6. Testar com arquivos pequenos primeiro",
            "7. Verificar formatos de arquivo suportados",
            "8. Considerar Evolution API como alternativa",
            "9. Verificar conectividade de rede",
            "10. Atualizar para versão mais recente do WAHA"
        ]
        
        for sugestao in sugestoes:
            print(f"   {sugestao}")
        
        print("\n📖 Consulte o arquivo GUIA_SOLUCAO_MIDIA_WAHA.md para detalhes")
    
    def menu_interativo(self) -> None:
        """Menu interativo principal"""
        while True:
            print("\n" + "=" * 60)
            print("🔧 SOLUCIONADOR DE PROBLEMAS DE MÍDIA - WAHA")
            print("=" * 60)
            print("\n📋 Opções disponíveis:")
            print("   1. 🔍 Diagnóstico completo")
            print("   2. ⚡ Verificação rápida de status")
            print("   3. 🧪 Testar formatos de mídia")
            print("   4. 📤 Testar envio de arquivo específico")
            print("   5. 🔍 Iniciar monitoramento em tempo real")
            print("   6. 🔧 Resolver problemas automaticamente")
            print("   7. ⚙️ Verificar/corrigir configuração")
            print("   8. 📖 Mostrar sugestões")
            print("   9. ❌ Sair")
            
            try:
                opcao = input("\n🎯 Escolha uma opção (1-9): ").strip()
                
                if opcao == '1':
                    self.executar_diagnostico_completo()
                
                elif opcao == '2':
                    self.verificar_status_rapido()
                
                elif opcao == '3':
                    self.testar_formatos_midia()
                
                elif opcao == '4':
                    arquivo = input("📁 Caminho do arquivo: ").strip()
                    if arquivo and os.path.exists(arquivo):
                        numero = input("📱 Número de teste (opcional): ").strip() or None
                        self.testar_formatos_midia(arquivo, numero)
                    else:
                        print("❌ Arquivo não encontrado")
                
                elif opcao == '5':
                    try:
                        intervalo = int(input("⏱️ Intervalo em segundos [30]: ").strip() or "30")
                        self.iniciar_monitoramento(intervalo)
                    except ValueError:
                        print("❌ Intervalo inválido")
                
                elif opcao == '6':
                    self.resolver_problemas_automaticamente()
                
                elif opcao == '7':
                    self.verificar_configuracao()
                
                elif opcao == '8':
                    self._mostrar_sugestoes_finais()
                
                elif opcao == '9':
                    print("\n👋 Saindo...")
                    break
                
                else:
                    print("❌ Opção inválida")
                
                input("\n⏸️ Pressione Enter para continuar...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Saindo...")
                break
            except Exception as e:
                print(f"\n❌ Erro: {e}")
                input("\n⏸️ Pressione Enter para continuar...")

def mostrar_ajuda():
    """Mostra ajuda do script"""
    print("🔧 Solucionador de Problemas de Mídia - WAHA")
    print("=" * 50)
    print("\n📖 USO:")
    print("  python solucionar_midia_waha.py                    # Menu interativo")
    print("  python solucionar_midia_waha.py --diagnostico      # Diagnóstico completo")
    print("  python solucionar_midia_waha.py --status           # Status rápido")
    print("  python solucionar_midia_waha.py --formatos         # Listar formatos")
    print("  python solucionar_midia_waha.py --monitor [tempo]  # Monitoramento")
    print("  python solucionar_midia_waha.py --resolver         # Resolver automaticamente")
    print("  python solucionar_midia_waha.py --config           # Verificar configuração")
    print("  python solucionar_midia_waha.py --teste arquivo    # Testar arquivo")
    print("\n📝 Exemplos:")
    print("  python solucionar_midia_waha.py --teste imagem.jpg")
    print("  python solucionar_midia_waha.py --monitor 60")
    print("\n📋 Arquivos necessários:")
    for script in ['diagnostico_midia_waha.py', 'teste_formatos_midia.py', 'monitor_waha_realtime.py']:
        status = "✅" if os.path.exists(script) else "❌"
        print(f"  {status} {script}")

def main():
    """Função principal"""
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        
        if comando in ['--help', '-h']:
            mostrar_ajuda()
            return
        
        solucionador = SolucionadorMidiaWAHA()
        
        if comando == '--diagnostico':
            solucionador.executar_diagnostico_completo()
        
        elif comando == '--status':
            solucionador.verificar_status_rapido()
        
        elif comando == '--formatos':
            solucionador.testar_formatos_midia()
        
        elif comando == '--monitor':
            intervalo = 30
            if len(sys.argv) > 2:
                try:
                    intervalo = int(sys.argv[2])
                except ValueError:
                    print("❌ Intervalo deve ser um número")
                    return
            solucionador.iniciar_monitoramento(intervalo)
        
        elif comando == '--resolver':
            solucionador.resolver_problemas_automaticamente()
        
        elif comando == '--config':
            solucionador.verificar_configuracao()
        
        elif comando == '--teste':
            if len(sys.argv) < 3:
                print("❌ Especifique o arquivo para teste")
                return
            
            arquivo = sys.argv[2]
            numero = sys.argv[3] if len(sys.argv) > 3 else None
            solucionador.testar_formatos_midia(arquivo, numero)
        
        else:
            print(f"❌ Comando desconhecido: {comando}")
            print("💡 Use --help para ver opções disponíveis")
    
    else:
        # Menu interativo
        solucionador = SolucionadorMidiaWAHA()
        solucionador.menu_interativo()

if __name__ == "__main__":
    main()