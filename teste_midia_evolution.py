#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Teste de Mídia - Evolution API
Testa o envio de diferentes tipos de mídia
"""

import requests
import json
import base64
import os
from datetime import datetime

class TesteMidiaEvolution:
    def __init__(self):
        self.config = {
            'base_url': 'http://localhost:8080',
            'token': 'evolution-api-key-2025',
            'instance_name': 'whatsapp-sender-v2'
        }
        self.headers = {'apikey': self.config['token']}
        self.resultados = []
    
    def criar_arquivo_teste(self, tipo='texto'):
        """Cria arquivos de teste para diferentes tipos de mídia"""
        os.makedirs('arquivos_teste', exist_ok=True)
        
        if tipo == 'texto':
            filename = 'arquivos_teste/teste.txt'
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('Este é um arquivo de teste para o WhatsApp\n')
                f.write(f'Criado em: {datetime.now()}\n')
            return filename
        
        elif tipo == 'imagem':
            # Criar uma imagem SVG simples
            filename = 'arquivos_teste/teste.svg'
            svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <rect width="200" height="200" fill="#4CAF50"/>
  <text x="100" y="100" font-family="Arial" font-size="16" fill="white" text-anchor="middle" dominant-baseline="middle">Teste WhatsApp</text>
  <text x="100" y="120" font-family="Arial" font-size="12" fill="white" text-anchor="middle" dominant-baseline="middle">''' + datetime.now().strftime('%d/%m/%Y %H:%M') + '''</text>
</svg>'''
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            return filename
        
        elif tipo == 'json':
            filename = 'arquivos_teste/teste.json'
            data = {
                'teste': True,
                'timestamp': datetime.now().isoformat(),
                'sistema': 'Evolution API',
                'tipo': 'arquivo_teste'
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return filename
    
    def verificar_instancia(self):
        """Verifica o status da instância"""
        print("🔍 Verificando instância...")
        
        try:
            url = f"{self.config['base_url']}/instance/connectionState/{self.config['instance_name']}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('state', 'Desconhecido')
                print(f"   ✅ Status da instância: {status}")
                return status
            else:
                print(f"   ❌ Erro ao verificar instância: {response.status_code}")
                return None
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
            return None
    
    def conectar_instancia(self):
        """Tenta conectar a instância se estiver desconectada"""
        print("🔗 Tentando conectar instância...")
        
        try:
            url = f"{self.config['base_url']}/instance/connect/{self.config['instance_name']}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Comando de conexão enviado")
                if 'qrcode' in data:
                    print(f"   📱 QR Code disponível: {data['qrcode']['code'][:50]}...")
                return True
            else:
                print(f"   ❌ Erro ao conectar: {response.status_code}")
                return False
        except requests.exceptions.Timeout:
            print(f"   ❌ Erro: Timeout na requisição")
            return False
        except requests.exceptions.Timeout:
            print(f"   ❌ Erro: Timeout na requisição")
            return False
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
            return False
    
    def testar_envio_texto(self, numero_teste='5511999999999'):
        """Testa envio de mensagem de texto"""
        print("\n📝 Testando envio de texto...")
        
        try:
            url = f"{self.config['base_url']}/message/sendText/{self.config['instance_name']}"
            
            payload = {
                'number': numero_teste,
                'text': f'🧪 Teste de mensagem - {datetime.now().strftime("%H:%M:%S")}'
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=60)
            
            resultado = {
                'tipo': 'texto',
                'status': response.status_code,
                'sucesso': response.status_code in [200, 201],
                'resposta': response.text[:200],
                'timestamp': datetime.now().isoformat()
            }
            
            self.resultados.append(resultado)
            
            if resultado['sucesso']:
                print(f"   ✅ Texto enviado com sucesso: {response.status_code}")
            else:
                print(f"   ❌ Erro no envio de texto: {response.status_code}")
                print(f"   📄 Resposta: {response.text[:100]}")
            
            return resultado['sucesso']
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
            return False
    
    def testar_envio_arquivo(self, arquivo, numero_teste='5511999999999'):
        """Testa envio de arquivo"""
        print(f"\n📎 Testando envio de arquivo: {os.path.basename(arquivo)}")
        
        try:
            # Ler arquivo e converter para base64
            with open(arquivo, 'rb') as f:
                file_data = f.read()
                file_base64 = base64.b64encode(file_data).decode('utf-8')
            
            # Determinar tipo MIME e mediatype
            if arquivo.endswith('.txt'):
                mimetype = 'text/plain'
                mediatype = 'document'
            elif arquivo.endswith('.svg'):
                mimetype = 'image/svg+xml'
                mediatype = 'image'
            elif arquivo.endswith('.json'):
                mimetype = 'application/json'
                mediatype = 'document'
            else:
                mimetype = 'application/octet-stream'
                mediatype = 'document'
            
            url = f"{self.config['base_url']}/message/sendMedia/{self.config['instance_name']}"
            
            payload = {
                'number': numero_teste,
                'media': file_base64,
                'fileName': os.path.basename(arquivo),
                'caption': f'📎 Arquivo de teste - {datetime.now().strftime("%H:%M:%S")}',
                'mediatype': mediatype
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=60)
            
            resultado = {
                'tipo': 'arquivo',
                'arquivo': os.path.basename(arquivo),
                'tamanho': len(file_data),
                'mimetype': mimetype,
                'mediatype': mediatype,
                'status': response.status_code,
                'sucesso': response.status_code in [200, 201],
                'resposta': response.text[:200],
                'timestamp': datetime.now().isoformat()
            }
            
            self.resultados.append(resultado)
            
            if resultado['sucesso']:
                print(f"   ✅ Arquivo enviado com sucesso: {response.status_code}")
                print(f"   📊 Tamanho: {len(file_data)} bytes")
            else:
                print(f"   ❌ Erro no envio de arquivo: {response.status_code}")
                print(f"   📄 Resposta: {response.text[:100]}")
            
            return resultado['sucesso']
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
            return False
    
    def gerar_relatorio(self):
        """Gera relatório dos testes"""
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE TESTES DE MÍDIA - EVOLUTION API")
        print("="*60)
        
        sucessos = sum(1 for r in self.resultados if r['sucesso'])
        total = len(self.resultados)
        
        print(f"\n📈 Resumo: {sucessos}/{total} testes bem-sucedidos")
        
        for resultado in self.resultados:
            status_icon = "✅" if resultado['sucesso'] else "❌"
            tipo = resultado['tipo'].title()
            
            if resultado['tipo'] == 'arquivo':
                print(f"   {status_icon} {tipo} ({resultado['arquivo']}): {resultado['status']}")
            else:
                print(f"   {status_icon} {tipo}: {resultado['status']}")
        
        # Salvar relatório
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"teste_midia_evolution_{timestamp}.json"
        
        relatorio_completo = {
            'config': self.config,
            'resultados': self.resultados,
            'resumo': {
                'total_testes': total,
                'sucessos': sucessos,
                'taxa_sucesso': f"{(sucessos/total*100):.1f}%" if total > 0 else "0%"
            },
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(relatorio_completo, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Relatório salvo em: {filename}")
        
        return sucessos == total

def main():
    print("🧪 TESTE DE MÍDIA - EVOLUTION API")
    print("Testando envio de diferentes tipos de arquivo...")
    
    testador = TesteMidiaEvolution()
    
    # Verificar instância
    status = testador.verificar_instancia()
    
    if status == 'close':
        print("\n⚠️ Instância desconectada. Tentando conectar...")
        testador.conectar_instancia()
        print("\n💡 Para conectar o WhatsApp:")
        print("   1. Acesse: http://localhost:8080")
        print("   2. Vá para a instância 'whatsapp-sender-v2'")
        print("   3. Escaneie o QR Code com seu WhatsApp")
        print("\n⏳ Aguardando conexão... (pressione Enter para continuar os testes)")
        input()
    
    # Criar arquivos de teste
    print("\n📁 Criando arquivos de teste...")
    arquivo_txt = testador.criar_arquivo_teste('texto')
    arquivo_svg = testador.criar_arquivo_teste('imagem')
    arquivo_json = testador.criar_arquivo_teste('json')
    
    print(f"   ✅ Criados: {arquivo_txt}, {arquivo_svg}, {arquivo_json}")
    
    # Executar testes
    print("\n🚀 Iniciando testes...")
    
    # Teste 1: Mensagem de texto
    testador.testar_envio_texto()
    
    # Teste 2: Arquivo de texto
    testador.testar_envio_arquivo(arquivo_txt)
    
    # Teste 3: Arquivo SVG
    testador.testar_envio_arquivo(arquivo_svg)
    
    # Teste 4: Arquivo JSON
    testador.testar_envio_arquivo(arquivo_json)
    
    # Gerar relatório
    sucesso_total = testador.gerar_relatorio()
    
    if sucesso_total:
        print("\n🎉 Todos os testes foram bem-sucedidos!")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique o relatório para detalhes.")
    
    print("\n✅ Testes concluídos!")

if __name__ == "__main__":
    main()