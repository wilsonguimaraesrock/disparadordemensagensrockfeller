#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Completo do Sistema
Verifica se todas as funcionalidades estão funcionando
"""

import os
import sys
import json
import time
from datetime import datetime
import subprocess


class TesteSistemaCompleto:
    def __init__(self):
        self.resultados = {
            'arquivos_principais': {},
            'configuracao': {},
            'apis': {},
            'funcionalidades': {},
            'resumo': {}
        }
        self.total_testes = 0
        self.testes_sucesso = 0
    
    def test(self, nome: str, funcao):
        """Executa um teste e registra resultado"""
        self.total_testes += 1
        print(f"\n🧪 Teste: {nome}")
        print("-" * 40)
        
        try:
            resultado = funcao()
            if resultado:
                print(f"✅ PASSOU: {nome}")
                self.testes_sucesso += 1
                return True
            else:
                print(f"❌ FALHOU: {nome}")
                return False
        except Exception as e:
            print(f"💥 ERRO: {nome} - {e}")
            return False
    
    def testar_arquivos_principais(self):
        """Testa se arquivos principais existem"""
        arquivos_essenciais = {
            'enviar_mensagens_lote.py': 'Script principal de envio',
            'api_sender.py': 'Módulo de comunicação com APIs',
            'utils.py': 'Utilitários do sistema',
            'config.json': 'Arquivo de configuração',
            'docker-compose.yml': 'Configuração Docker'
        }
        
        for arquivo, descricao in arquivos_essenciais.items():
            if os.path.exists(arquivo):
                tamanho = os.path.getsize(arquivo)
                if tamanho > 0:
                    print(f"✅ {arquivo}: {tamanho} bytes - {descricao}")
                    self.resultados['arquivos_principais'][arquivo] = True
                else:
                    print(f"⚠️  {arquivo}: vazio! - {descricao}")
                    self.resultados['arquivos_principais'][arquivo] = False
            else:
                print(f"❌ {arquivo}: não encontrado - {descricao}")
                self.resultados['arquivos_principais'][arquivo] = False
        
        return all(self.resultados['arquivos_principais'].values())
    
    def testar_configuracao(self):
        """Testa se configuração está válida"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            campos_obrigatorios = ['provider', 'base_url', 'instance_id', 'token']
            
            for campo in campos_obrigatorios:
                if campo in config and config[campo]:
                    print(f"✅ {campo}: {config[campo]}")
                    self.resultados['configuracao'][campo] = True
                else:
                    print(f"❌ {campo}: ausente ou vazio")
                    self.resultados['configuracao'][campo] = False
            
            # Verificar provider
            provider = config.get('provider', '').lower()
            if provider == 'evolution-api':
                print(f"✅ Provider configurado: Evolution API")
            elif provider == 'waha':
                print(f"⚠️  Provider configurado: WAHA (limitações de mídia)")
            else:
                print(f"❌ Provider desconhecido: {provider}")
            
            return all(self.resultados['configuracao'].values())
            
        except FileNotFoundError:
            print("❌ config.json não encontrado")
            return False
        except json.JSONDecodeError:
            print("❌ config.json com formato inválido")
            return False
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def testar_imports(self):
        """Testa se módulos podem ser importados"""
        modulos = {
            'utils': 'Utilitários',
            'api_sender': 'Sender de API'
        }
        
        for modulo, descricao in modulos.items():
            try:
                __import__(modulo)
                print(f"✅ {modulo}: importado com sucesso - {descricao}")
            except ImportError as e:
                print(f"❌ {modulo}: erro de importação - {e}")
                return False
            except Exception as e:
                print(f"⚠️  {modulo}: erro inesperado - {e}")
        
        return True
    
    def testar_api_evolution(self):
        """Testa conectividade com Evolution API"""
        try:
            import requests
            
            with open('config.json', 'r') as f:
                config = json.load(f)
            
            if config.get('provider') != 'evolution-api':
                print("⚠️  Provider não é Evolution API, pulando teste")
                return True
            
            base_url = config.get('base_url', 'http://localhost:8080')
            
            # Teste de conectividade básica
            print(f"🔌 Testando conectividade: {base_url}")
            response = requests.get(f"{base_url}/", timeout=5)
            
            if response.status_code == 200:
                print(f"✅ Evolution API respondendo")
                self.resultados['apis']['evolution_conectividade'] = True
            else:
                print(f"⚠️  Evolution API respondeu com status {response.status_code}")
                self.resultados['apis']['evolution_conectividade'] = False
            
            # Teste de autenticação
            api_key = config.get('token', '')
            headers = {'apikey': api_key}
            
            print(f"🔐 Testando autenticação...")
            response = requests.get(f"{base_url}/instance/fetchInstances", 
                                  headers=headers, timeout=5)
            
            if response.status_code == 200:
                instances = response.json()
                print(f"✅ Autenticação OK - {len(instances)} instâncias encontradas")
                self.resultados['apis']['evolution_auth'] = True
                
                # Verificar instância específica
                instance_id = config.get('instance_id', '')
                for inst in instances:
                    if inst.get('name') == instance_id:
                        status = inst.get('connectionStatus', 'unknown')
                        print(f"📱 Instância '{instance_id}': {status}")
                        break
                else:
                    print(f"⚠️  Instância '{instance_id}' não encontrada")
                
            else:
                print(f"❌ Falha na autenticação: {response.status_code}")
                self.resultados['apis']['evolution_auth'] = False
            
            return self.resultados['apis'].get('evolution_conectividade', False)
            
        except requests.exceptions.ConnectionError:
            print(f"❌ Não foi possível conectar em {base_url}")
            print("💡 Evolution API não está rodando ou URL incorreta")
            self.resultados['apis']['evolution_conectividade'] = False
            return False
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def testar_arquivos_exemplo(self):
        """Testa se arquivos de exemplo existem"""
        pasta_teste = 'arquivos_teste'
        
        if not os.path.exists(pasta_teste):
            print(f"📁 Pasta {pasta_teste} não existe")
            return False
        
        arquivos_teste = ['teste.txt', 'teste.svg', 'teste.json']
        encontrados = 0
        
        for arquivo in arquivos_teste:
            caminho = os.path.join(pasta_teste, arquivo)
            if os.path.exists(caminho):
                tamanho = os.path.getsize(caminho)
                print(f"✅ {arquivo}: {tamanho} bytes")
                encontrados += 1
            else:
                print(f"❌ {arquivo}: não encontrado")
        
        if encontrados > 0:
            print(f"✅ {encontrados}/{len(arquivos_teste)} arquivos de teste encontrados")
            return True
        else:
            print("❌ Nenhum arquivo de teste encontrado")
            return False
    
    def testar_dependencias_python(self):
        """Testa dependências Python"""
        dependencias = {
            'requests': 'Requisições HTTP',
            'pandas': 'Manipulação de Excel (opcional)',
            'openpyxl': 'Leitura de Excel (opcional)'
        }
        
        obrigatorias = ['requests']
        encontradas = 0
        
        for lib, descricao in dependencias.items():
            try:
                __import__(lib)
                print(f"✅ {lib}: instalado - {descricao}")
                encontradas += 1
            except ImportError:
                if lib in obrigatorias:
                    print(f"❌ {lib}: OBRIGATÓRIO - {descricao}")
                else:
                    print(f"⚠️  {lib}: opcional - {descricao}")
        
        return encontradas >= len(obrigatorias)
    
    def executar_teste_simples(self):
        """Executa teste simples do sistema principal"""
        try:
            print("🔄 Testando importação do sistema principal...")
            from enviar_mensagens_lote import verificar_sistema
            
            print("🔄 Executando verificação do sistema...")
            resultado = verificar_sistema()
            
            if resultado:
                print("✅ Sistema principal funcionando")
                return True
            else:
                print("❌ Sistema principal com problemas")
                return False
                
        except ImportError as e:
            print(f"❌ Erro de importação: {e}")
            return False
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def gerar_relatorio(self):
        """Gera relatório final dos testes"""
        self.resultados['resumo'] = {
            'total_testes': self.total_testes,
            'testes_sucesso': self.testes_sucesso,
            'taxa_sucesso': (self.testes_sucesso / self.total_testes * 100) if self.total_testes > 0 else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        # Salvar relatório
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'relatorio_teste_sistema_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.resultados, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório salvo: {filename}")
        return filename
    
    def mostrar_resumo_final(self):
        """Mostra resumo final dos testes"""
        print("\n" + "=" * 60)
        print("📊 RESUMO FINAL DOS TESTES")
        print("=" * 60)
        
        taxa_sucesso = (self.testes_sucesso / self.total_testes * 100) if self.total_testes > 0 else 0
        
        print(f"📋 Total de testes: {self.total_testes}")
        print(f"✅ Testes passou: {self.testes_sucesso}")
        print(f"❌ Testes falhou: {self.total_testes - self.testes_sucesso}")
        print(f"📈 Taxa de sucesso: {taxa_sucesso:.1f}%")
        
        if taxa_sucesso >= 90:
            print("🎉 EXCELENTE! Sistema funcionando perfeitamente!")
        elif taxa_sucesso >= 75:
            print("👍 BOM! Sistema funcionando com pequenos problemas.")
        elif taxa_sucesso >= 50:
            print("⚠️  MODERADO! Sistema precisa de ajustes.")
        else:
            print("🚨 CRÍTICO! Sistema com muitos problemas!")
        
        print("\n💡 PRÓXIMOS PASSOS:")
        if taxa_sucesso < 100:
            print("1. Revisar itens que falharam nos testes")
            print("2. Instalar dependências em falta")
            print("3. Configurar APIs necessárias")
            print("4. Executar testes novamente")
        else:
            print("1. python criar_excel_exemplo.py")
            print("2. python enviar_mensagens_lote.py")
            print("3. Testar envio com arquivo de exemplo")


def main():
    print("🧪 TESTE COMPLETO DO SISTEMA")
    print("=" * 60)
    print("Verificando todas as funcionalidades do disparador...")
    print("")
    
    tester = TesteSistemaCompleto()
    
    # Executar todos os testes
    testes = [
        ("Arquivos Principais", tester.testar_arquivos_principais),
        ("Configuração", tester.testar_configuracao),
        ("Importações", tester.testar_imports),
        ("Dependências Python", tester.testar_dependencias_python),
        ("API Evolution", tester.testar_api_evolution),
        ("Arquivos de Exemplo", tester.testar_arquivos_exemplo),
        ("Sistema Principal", tester.executar_teste_simples)
    ]
    
    for nome, funcao in testes:
        tester.test(nome, funcao)
    
    # Gerar relatório e mostrar resumo
    tester.gerar_relatorio()
    tester.mostrar_resumo_final()


if __name__ == "__main__":
    main()