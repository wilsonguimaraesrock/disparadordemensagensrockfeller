#!/usr/bin/env python3
"""
Script de Diagnóstico Automatizado para Problemas de Mídia no WAHA
Este script identifica e resolve automaticamente problemas comuns de envio de mídia.
"""

import os
import sys
import json
import time
import requests
import mimetypes
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class DiagnosticoWAHA:
    def __init__(self, config_path: str = "config.json"):
        self.config = self._carregar_config(config_path)
        self.base_url = self.config.get('base_url', 'http://localhost:3000')
        self.token = self.config.get('token', '')
        self.instance_id = self.config.get('instance_id', 'default')
        self.headers = {'X-API-KEY': self.token}
        self.problemas_encontrados = []
        self.solucoes_aplicadas = []
        
    def _carregar_config(self, config_path: str) -> Dict:
        """Carrega configurações do arquivo JSON"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Arquivo de configuração não encontrado: {config_path}")
            return {}
        except json.JSONDecodeError:
            print(f"❌ Erro ao decodificar JSON: {config_path}")
            return {}
    
    def executar_diagnostico_completo(self) -> Dict:
        """Executa diagnóstico completo do sistema"""
        print("🔍 Iniciando Diagnóstico Completo do WAHA")
        print("=" * 50)
        
        resultados = {
            'timestamp': datetime.now().isoformat(),
            'config_valida': False,
            'waha_online': False,
            'sessao_ativa': False,
            'token_valido': False,
            'endpoints_funcionando': False,
            'problemas': [],
            'solucoes': [],
            'recomendacoes': []
        }
        
        # 1. Verificar configuração
        print("\n1️⃣ Verificando Configuração...")
        resultados['config_valida'] = self._verificar_configuracao()
        
        # 2. Verificar conectividade com WAHA
        print("\n2️⃣ Verificando Conectividade...")
        resultados['waha_online'] = self._verificar_conectividade()
        
        # 3. Verificar token de API
        print("\n3️⃣ Verificando Token de API...")
        resultados['token_valido'] = self._verificar_token()
        
        # 4. Verificar status da sessão
        print("\n4️⃣ Verificando Status da Sessão...")
        resultados['sessao_ativa'] = self._verificar_sessao()
        
        # 5. Testar endpoints de mídia
        print("\n5️⃣ Testando Endpoints de Mídia...")
        resultados['endpoints_funcionando'] = self._testar_endpoints()
        
        # 6. Gerar relatório
        print("\n6️⃣ Gerando Relatório...")
        self._gerar_relatorio(resultados)
        
        return resultados
    
    def _verificar_configuracao(self) -> bool:
        """Verifica se a configuração está correta"""
        problemas_config = []
        
        if not self.base_url:
            problemas_config.append("Base URL não configurada")
        
        if not self.token:
            problemas_config.append("Token de API não configurado")
        
        if not self.instance_id:
            problemas_config.append("Instance ID não configurado")
        
        if self.config.get('provider', '').lower() != 'waha':
            problemas_config.append("Provider não está configurado como 'waha'")
        
        if problemas_config:
            print(f"❌ Problemas de configuração encontrados:")
            for problema in problemas_config:
                print(f"   • {problema}")
            self.problemas_encontrados.extend(problemas_config)
            return False
        else:
            print("✅ Configuração válida")
            return True
    
    def _verificar_conectividade(self) -> bool:
        """Verifica se o WAHA está online"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            if response.status_code == 200:
                print("✅ WAHA está online")
                return True
            else:
                print(f"❌ WAHA respondeu com status {response.status_code}")
                self.problemas_encontrados.append(f"WAHA status: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Não foi possível conectar ao WAHA")
            self.problemas_encontrados.append("WAHA não está rodando ou inacessível")
            return False
        except requests.exceptions.Timeout:
            print("❌ Timeout ao conectar com WAHA")
            self.problemas_encontrados.append("Timeout de conexão com WAHA")
            return False
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            self.problemas_encontrados.append(f"Erro de conexão: {e}")
            return False
    
    def _verificar_token(self) -> bool:
        """Verifica se o token de API é válido"""
        try:
            response = requests.get(f"{self.base_url}/api/sessions", 
                                  headers=self.headers, timeout=10)
            if response.status_code == 200:
                print("✅ Token de API válido")
                return True
            elif response.status_code == 401:
                print("❌ Token de API inválido ou expirado")
                self.problemas_encontrados.append("Token de API inválido")
                return False
            else:
                print(f"❌ Erro ao validar token: {response.status_code}")
                self.problemas_encontrados.append(f"Erro de validação do token: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro ao verificar token: {e}")
            self.problemas_encontrados.append(f"Erro na verificação do token: {e}")
            return False
    
    def _verificar_sessao(self) -> bool:
        """Verifica se a sessão WhatsApp está ativa"""
        try:
            response = requests.get(f"{self.base_url}/api/sessions/{self.instance_id}", 
                                  headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'UNKNOWN')
                print(f"📱 Status da sessão: {status}")
                
                if status == 'WORKING':
                    print("✅ Sessão WhatsApp ativa")
                    return True
                elif status == 'SCAN_QR_CODE':
                    print("📱 Sessão aguardando QR Code")
                    self.problemas_encontrados.append("Sessão precisa escanear QR Code")
                    return False
                elif status == 'FAILED':
                    print("❌ Sessão falhou")
                    self.problemas_encontrados.append("Sessão WhatsApp falhou")
                    return False
                else:
                    print(f"⚠️ Status desconhecido: {status}")
                    self.problemas_encontrados.append(f"Status da sessão: {status}")
                    return False
            elif response.status_code == 404:
                print("❌ Sessão não encontrada")
                self.problemas_encontrados.append("Sessão não existe")
                return False
            else:
                print(f"❌ Erro ao verificar sessão: {response.status_code}")
                self.problemas_encontrados.append(f"Erro na verificação da sessão: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro ao verificar sessão: {e}")
            self.problemas_encontrados.append(f"Erro na verificação da sessão: {e}")
            return False
    
    def _testar_endpoints(self) -> bool:
        """Testa os endpoints de envio de mídia"""
        endpoints = [
            '/api/sendImage',
            '/api/sendVideo', 
            '/api/sendVoice',
            '/api/sendFile'
        ]
        
        endpoints_funcionando = 0
        
        for endpoint in endpoints:
            try:
                # Fazer uma requisição OPTIONS para verificar se o endpoint existe
                response = requests.options(f"{self.base_url}{endpoint}", 
                                          headers=self.headers, timeout=5)
                if response.status_code in [200, 405]:  # 405 = Method Not Allowed (mas endpoint existe)
                    print(f"✅ Endpoint {endpoint} disponível")
                    endpoints_funcionando += 1
                else:
                    print(f"❌ Endpoint {endpoint} não disponível ({response.status_code})")
                    self.problemas_encontrados.append(f"Endpoint {endpoint} não funciona")
            except Exception as e:
                print(f"❌ Erro ao testar {endpoint}: {e}")
                self.problemas_encontrados.append(f"Erro no endpoint {endpoint}: {e}")
        
        if endpoints_funcionando == len(endpoints):
            print("✅ Todos os endpoints de mídia estão funcionando")
            return True
        else:
            print(f"⚠️ {endpoints_funcionando}/{len(endpoints)} endpoints funcionando")
            return False
    
    def _gerar_relatorio(self, resultados: Dict) -> None:
        """Gera relatório detalhado do diagnóstico"""
        print("\n" + "=" * 50)
        print("📊 RELATÓRIO DE DIAGNÓSTICO")
        print("=" * 50)
        
        # Status geral
        status_geral = all([
            resultados['config_valida'],
            resultados['waha_online'],
            resultados['token_valido'],
            resultados['sessao_ativa']
        ])
        
        if status_geral:
            print("🎉 Sistema funcionando corretamente!")
        else:
            print("⚠️ Problemas encontrados que precisam ser corrigidos")
        
        # Detalhes dos testes
        print("\n📋 Resultados dos Testes:")
        print(f"   • Configuração: {'✅' if resultados['config_valida'] else '❌'}")
        print(f"   • WAHA Online: {'✅' if resultados['waha_online'] else '❌'}")
        print(f"   • Token Válido: {'✅' if resultados['token_valido'] else '❌'}")
        print(f"   • Sessão Ativa: {'✅' if resultados['sessao_ativa'] else '❌'}")
        print(f"   • Endpoints: {'✅' if resultados['endpoints_funcionando'] else '❌'}")
        
        # Problemas encontrados
        if self.problemas_encontrados:
            print("\n🚨 Problemas Encontrados:")
            for i, problema in enumerate(self.problemas_encontrados, 1):
                print(f"   {i}. {problema}")
        
        # Recomendações
        recomendacoes = self._gerar_recomendacoes(resultados)
        if recomendacoes:
            print("\n💡 Recomendações:")
            for i, recomendacao in enumerate(recomendacoes, 1):
                print(f"   {i}. {recomendacao}")
        
        # Salvar relatório em arquivo
        self._salvar_relatorio(resultados, recomendacoes)
    
    def _gerar_recomendacoes(self, resultados: Dict) -> List[str]:
        """Gera recomendações baseadas nos problemas encontrados"""
        recomendacoes = []
        
        if not resultados['config_valida']:
            recomendacoes.append("Verificar e corrigir o arquivo config.json")
        
        if not resultados['waha_online']:
            recomendacoes.append("Iniciar o WAHA: docker-compose up -d")
            recomendacoes.append("Verificar se a porta 3000 está disponível")
        
        if not resultados['token_valido']:
            recomendacoes.append("Verificar se o token de API está correto no config.json")
            recomendacoes.append("Gerar um novo token se necessário")
        
        if not resultados['sessao_ativa']:
            recomendacoes.append("Escanear o QR Code para conectar o WhatsApp")
            recomendacoes.append("Reiniciar a sessão se estiver com falha")
        
        if not resultados['endpoints_funcionando']:
            recomendacoes.append("Atualizar para WAHA Plus para suporte completo a mídia")
            recomendacoes.append("Usar a imagem Docker: devlikeapro/waha-plus:chrome")
        
        # Recomendações gerais
        recomendacoes.extend([
            "Verificar os logs do Docker: docker logs container_waha",
            "Testar com arquivos pequenos primeiro",
            "Considerar usar Evolution API como alternativa"
        ])
        
        return recomendacoes
    
    def _salvar_relatorio(self, resultados: Dict, recomendacoes: List[str]) -> None:
        """Salva o relatório em arquivo JSON"""
        relatorio = {
            **resultados,
            'problemas': self.problemas_encontrados,
            'recomendacoes': recomendacoes
        }
        
        filename = f"diagnostico_waha_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(relatorio, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Relatório salvo em: {filename}")
        except Exception as e:
            print(f"\n❌ Erro ao salvar relatório: {e}")
    
    def testar_envio_midia(self, numero_teste: str, arquivo_teste: str) -> bool:
        """Testa o envio de mídia com um arquivo específico"""
        print(f"\n🧪 Testando envio de mídia para {numero_teste}")
        
        if not os.path.exists(arquivo_teste):
            print(f"❌ Arquivo não encontrado: {arquivo_teste}")
            return False
        
        # Verificar tipo de arquivo
        mime_type, _ = mimetypes.guess_type(arquivo_teste)
        print(f"📄 Tipo de arquivo: {mime_type}")
        
        # Verificar tamanho
        tamanho_mb = os.path.getsize(arquivo_teste) / (1024 * 1024)
        print(f"📏 Tamanho: {tamanho_mb:.2f} MB")
        
        if tamanho_mb > 16:
            print("❌ Arquivo muito grande (limite: 16MB)")
            return False
        
        # Determinar endpoint
        if mime_type and mime_type.startswith('image/'):
            endpoint = "/api/sendImage"
        elif mime_type and mime_type.startswith('video/'):
            endpoint = "/api/sendVideo"
        elif mime_type and mime_type.startswith('audio/'):
            endpoint = "/api/sendVoice"
        else:
            endpoint = "/api/sendFile"
        
        print(f"🎯 Usando endpoint: {endpoint}")
        
        # Tentar enviar
        try:
            url = f"{self.base_url}{endpoint}"
            
            with open(arquivo_teste, 'rb') as file:
                files = {'file': file}
                data = {
                    'chatId': f"{numero_teste.replace('+', '')}@c.us",
                    'caption': 'Teste de envio de mídia - Diagnóstico WAHA',
                    'session': self.instance_id
                }
                
                headers = self.headers.copy()
                if 'Content-Type' in headers:
                    del headers['Content-Type']
                
                print("📤 Enviando arquivo...")
                response = requests.post(url, files=files, data=data, 
                                       headers=headers, timeout=60)
                
                if response.status_code in [200, 201]:
                    try:
                        result = response.json()
                        if response.status_code == 201 or result.get('success', False):
                            print("✅ Mídia enviada com sucesso!")
                            return True
                        else:
                            error_msg = result.get('message', 'Erro desconhecido')
                            print(f"❌ Falha no envio: {error_msg}")
                            return False
                    except json.JSONDecodeError:
                        print("❌ Resposta inválida do servidor")
                        return False
                else:
                    print(f"❌ Erro HTTP: {response.status_code}")
                    try:
                        error_detail = response.json()
                        print(f"   Detalhes: {error_detail}")
                    except:
                        print(f"   Resposta: {response.text[:200]}")
                    return False
                    
        except Exception as e:
            print(f"❌ Erro durante o envio: {e}")
            return False
    
    def corrigir_problemas_automaticamente(self) -> None:
        """Tenta corrigir problemas automaticamente"""
        print("\n🔧 Tentando corrigir problemas automaticamente...")
        
        # Tentar reiniciar sessão se estiver com problema
        if "Sessão WhatsApp falhou" in self.problemas_encontrados:
            print("🔄 Tentando reiniciar sessão...")
            if self._reiniciar_sessao():
                print("✅ Sessão reiniciada com sucesso")
                self.solucoes_aplicadas.append("Sessão reiniciada")
            else:
                print("❌ Falha ao reiniciar sessão")
        
        # Outras correções automáticas podem ser adicionadas aqui
    
    def _reiniciar_sessao(self) -> bool:
        """Reinicia a sessão WAHA"""
        try:
            # Parar sessão atual
            stop_url = f"{self.base_url}/api/sessions/{self.instance_id}/stop"
            response = requests.post(stop_url, headers=self.headers, timeout=10)
            
            time.sleep(3)  # Aguardar parada completa
            
            # Iniciar nova sessão
            start_url = f"{self.base_url}/api/sessions/start"
            payload = {
                "name": self.instance_id,
                "config": {
                    "proxy": None,
                    "webhooks": []
                }
            }
            response = requests.post(start_url, json=payload, 
                                   headers=self.headers, timeout=30)
            return response.status_code == 201
        except Exception as e:
            print(f"Erro ao reiniciar sessão: {e}")
            return False

def main():
    """Função principal"""
    print("🚀 Diagnóstico Automatizado WAHA - Problemas de Mídia")
    print("=" * 60)
    
    # Verificar se arquivo de configuração existe
    if not os.path.exists('config.json'):
        print("❌ Arquivo config.json não encontrado!")
        print("💡 Crie o arquivo config.json com as configurações do WAHA")
        return
    
    # Inicializar diagnóstico
    diagnostico = DiagnosticoWAHA()
    
    # Executar diagnóstico completo
    resultados = diagnostico.executar_diagnostico_completo()
    
    # Tentar correções automáticas
    diagnostico.corrigir_problemas_automaticamente()
    
    # Teste opcional de envio
    if len(sys.argv) > 2:
        numero_teste = sys.argv[1]
        arquivo_teste = sys.argv[2]
        print(f"\n🧪 Executando teste de envio...")
        diagnostico.testar_envio_midia(numero_teste, arquivo_teste)
    
    print("\n✅ Diagnóstico concluído!")
    print("📖 Consulte o guia GUIA_SOLUCAO_MIDIA_WAHA.md para mais detalhes")

if __name__ == "__main__":
    main()