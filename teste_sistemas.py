#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Teste dos Sistemas WAHA e Evolution API
Testa conectividade, autenticação e funcionalidades básicas
"""

import requests
import json
import time
from datetime import datetime

class TestadorSistemas:
    def __init__(self):
        self.resultados = {
            'waha': {},
            'evolution': {},
            'timestamp': datetime.now().isoformat()
        }
    
    def testar_waha(self):
        """Testa o sistema WAHA"""
        print("\n🔍 Testando WAHA...")
        
        config = {
            'base_url': 'http://localhost:3000',
            'token': 'waha-key-2025',
            'instance_id': 'default'
        }
        
        headers = {'X-API-Key': config['token']}
        
        # Teste 1: Conectividade
        try:
            response = requests.get(f"{config['base_url']}/api/version", headers=headers, timeout=5)
            self.resultados['waha']['conectividade'] = {
                'status': response.status_code,
                'sucesso': response.status_code == 200,
                'resposta': response.text[:200] if response.text else 'Sem resposta'
            }
            print(f"   ✅ Conectividade: {response.status_code}")
        except Exception as e:
            self.resultados['waha']['conectividade'] = {
                'status': 'erro',
                'sucesso': False,
                'erro': str(e)
            }
            print(f"   ❌ Conectividade: {str(e)}")
        
        # Teste 2: Listar sessões
        try:
            response = requests.get(f"{config['base_url']}/api/sessions", headers=headers, timeout=5)
            self.resultados['waha']['sessoes'] = {
                'status': response.status_code,
                'sucesso': response.status_code == 200,
                'dados': response.json() if response.status_code == 200 else response.text
            }
            print(f"   ✅ Sessões: {response.status_code}")
        except Exception as e:
            self.resultados['waha']['sessoes'] = {
                'status': 'erro',
                'sucesso': False,
                'erro': str(e)
            }
            print(f"   ❌ Sessões: {str(e)}")
        
        # Teste 3: Status da sessão default
        try:
            response = requests.get(f"{config['base_url']}/api/sessions/{config['instance_id']}", headers=headers, timeout=5)
            self.resultados['waha']['status_sessao'] = {
                'status': response.status_code,
                'sucesso': response.status_code == 200,
                'dados': response.json() if response.status_code == 200 else response.text
            }
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status da sessão: {data.get('status', 'Desconhecido')}")
            else:
                print(f"   ❌ Status da sessão: {response.status_code}")
        except Exception as e:
            self.resultados['waha']['status_sessao'] = {
                'status': 'erro',
                'sucesso': False,
                'erro': str(e)
            }
            print(f"   ❌ Status da sessão: {str(e)}")
    
    def testar_evolution(self):
        """Testa o sistema Evolution API"""
        print("\n🔍 Testando Evolution API...")
        
        config = {
            'base_url': 'http://localhost:8080',
            'token': 'evolution-api-key-2025'
        }
        
        headers = {'apikey': config['token']}
        
        # Teste 1: Conectividade
        try:
            response = requests.get(f"{config['base_url']}/manager/status", headers=headers, timeout=5)
            self.resultados['evolution']['conectividade'] = {
                'status': response.status_code,
                'sucesso': response.status_code == 200,
                'resposta': response.text[:200] if response.text else 'Sem resposta'
            }
            print(f"   ✅ Conectividade: {response.status_code}")
        except Exception as e:
            self.resultados['evolution']['conectividade'] = {
                'status': 'erro',
                'sucesso': False,
                'erro': str(e)
            }
            print(f"   ❌ Conectividade: {str(e)}")
        
        # Teste 2: Listar instâncias
        try:
            response = requests.get(f"{config['base_url']}/instance/fetchInstances", headers=headers, timeout=5)
            self.resultados['evolution']['instancias'] = {
                'status': response.status_code,
                'sucesso': response.status_code == 200,
                'dados': response.json() if response.status_code == 200 else response.text
            }
            if response.status_code == 200:
                instancias = response.json()
                print(f"   ✅ Instâncias encontradas: {len(instancias)}")
                for inst in instancias:
                    print(f"      - {inst.get('name', 'Sem nome')}: {inst.get('connectionStatus', 'Desconhecido')}")
            else:
                print(f"   ❌ Instâncias: {response.status_code}")
        except Exception as e:
            self.resultados['evolution']['instancias'] = {
                'status': 'erro',
                'sucesso': False,
                'erro': str(e)
            }
            print(f"   ❌ Instâncias: {str(e)}")
        
        # Teste 3: Verificar instância específica
        try:
            response = requests.get(f"{config['base_url']}/instance/connectionState/whatsapp-sender-v2", headers=headers, timeout=5)
            self.resultados['evolution']['status_instancia'] = {
                'status': response.status_code,
                'sucesso': response.status_code == 200,
                'dados': response.json() if response.status_code == 200 else response.text
            }
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status da instância: {data.get('state', 'Desconhecido')}")
            else:
                print(f"   ❌ Status da instância: {response.status_code}")
        except Exception as e:
            self.resultados['evolution']['status_instancia'] = {
                'status': 'erro',
                'sucesso': False,
                'erro': str(e)
            }
            print(f"   ❌ Status da instância: {str(e)}")
    
    def gerar_relatorio(self):
        """Gera relatório dos testes"""
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE TESTES DOS SISTEMAS")
        print("="*60)
        
        # Resumo WAHA
        print("\n🔧 WAHA:")
        waha_ok = 0
        waha_total = 0
        for teste, resultado in self.resultados['waha'].items():
            waha_total += 1
            if resultado.get('sucesso', False):
                waha_ok += 1
                print(f"   ✅ {teste.replace('_', ' ').title()}")
            else:
                print(f"   ❌ {teste.replace('_', ' ').title()}")
        
        # Resumo Evolution
        print("\n🚀 Evolution API:")
        evo_ok = 0
        evo_total = 0
        for teste, resultado in self.resultados['evolution'].items():
            evo_total += 1
            if resultado.get('sucesso', False):
                evo_ok += 1
                print(f"   ✅ {teste.replace('_', ' ').title()}")
            else:
                print(f"   ❌ {teste.replace('_', ' ').title()}")
        
        # Recomendações
        print("\n💡 RECOMENDAÇÕES:")
        
        if waha_ok == waha_total:
            print("   🎉 WAHA está funcionando perfeitamente!")
        elif waha_ok > 0:
            print("   ⚠️ WAHA está parcialmente funcional - verificar problemas")
        else:
            print("   🚨 WAHA não está funcionando - verificar configuração")
        
        if evo_ok == evo_total:
            print("   🎉 Evolution API está funcionando perfeitamente!")
        elif evo_ok > 0:
            print("   ⚠️ Evolution API está parcialmente funcional - verificar problemas")
        else:
            print("   🚨 Evolution API não está funcionando - verificar configuração")
        
        # Salvar relatório
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"teste_sistemas_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.resultados, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Relatório salvo em: {filename}")
        
        return {
            'waha_score': f"{waha_ok}/{waha_total}",
            'evolution_score': f"{evo_ok}/{evo_total}",
            'melhor_sistema': 'Evolution API' if evo_ok > waha_ok else 'WAHA' if waha_ok > evo_ok else 'Empate'
        }

def main():
    print("🧪 TESTE DE SISTEMAS WHATSAPP")
    print("Verificando WAHA e Evolution API...")
    
    testador = TestadorSistemas()
    
    # Executar testes
    testador.testar_waha()
    testador.testar_evolution()
    
    # Gerar relatório
    resultado = testador.gerar_relatorio()
    
    print(f"\n🏆 Sistema recomendado: {resultado['melhor_sistema']}")
    print("\n✅ Testes concluídos!")

if __name__ == "__main__":
    main()