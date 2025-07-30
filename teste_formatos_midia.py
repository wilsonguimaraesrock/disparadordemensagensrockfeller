#!/usr/bin/env python3
"""
Script de Teste de Formatos de Mídia para WAHA
Testa diferentes tipos e formatos de mídia suportados pelo WhatsApp via WAHA
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

class TesteFormatosMidia:
    def __init__(self, config_path: str = "config.json"):
        self.config = self._carregar_config(config_path)
        self.base_url = self.config.get('base_url', 'http://localhost:3000')
        self.token = self.config.get('token', '')
        self.instance_id = self.config.get('instance_id', 'default')
        self.headers = {'X-API-KEY': self.token}
        
        # Formatos suportados pelo WhatsApp
        self.formatos_suportados = {
            'imagem': {
                'tipos': ['image/jpeg', 'image/png', 'image/webp'],
                'extensoes': ['.jpg', '.jpeg', '.png', '.webp'],
                'limite_mb': 16,
                'endpoint': '/api/sendImage'
            },
            'video': {
                'tipos': ['video/mp4', 'video/3gpp'],
                'extensoes': ['.mp4', '.3gp'],
                'limite_mb': 16,
                'endpoint': '/api/sendVideo',
                'observacoes': 'Apenas MP4 com codec H.264'
            },
            'audio': {
                'tipos': ['audio/aac', 'audio/mp4', 'audio/mpeg', 'audio/amr', 'audio/ogg'],
                'extensoes': ['.aac', '.m4a', '.mp3', '.amr', '.ogg'],
                'limite_mb': 16,
                'endpoint': '/api/sendVoice'
            },
            'documento': {
                'tipos': ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                         'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         'text/plain', 'application/zip'],
                'extensoes': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.zip'],
                'limite_mb': 100,
                'endpoint': '/api/sendFile'
            }
        }
    
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
    
    def verificar_formato_arquivo(self, caminho_arquivo: str) -> Dict:
        """Verifica se o formato do arquivo é suportado"""
        if not os.path.exists(caminho_arquivo):
            return {'valido': False, 'erro': 'Arquivo não encontrado'}
        
        # Obter informações do arquivo
        nome_arquivo = os.path.basename(caminho_arquivo)
        extensao = Path(caminho_arquivo).suffix.lower()
        mime_type, _ = mimetypes.guess_type(caminho_arquivo)
        tamanho_bytes = os.path.getsize(caminho_arquivo)
        tamanho_mb = tamanho_bytes / (1024 * 1024)
        
        resultado = {
            'nome': nome_arquivo,
            'extensao': extensao,
            'mime_type': mime_type,
            'tamanho_mb': round(tamanho_mb, 2),
            'tamanho_bytes': tamanho_bytes,
            'valido': False,
            'categoria': None,
            'endpoint': None,
            'problemas': []
        }
        
        # Verificar categoria e suporte
        categoria_encontrada = None
        for categoria, info in self.formatos_suportados.items():
            if extensao in info['extensoes'] or (mime_type and mime_type in info['tipos']):
                categoria_encontrada = categoria
                resultado['categoria'] = categoria
                resultado['endpoint'] = info['endpoint']
                
                # Verificar limite de tamanho
                if tamanho_mb > info['limite_mb']:
                    resultado['problemas'].append(f"Arquivo muito grande: {tamanho_mb:.2f}MB (limite: {info['limite_mb']}MB)")
                
                # Verificações específicas por categoria
                if categoria == 'video':
                    if extensao not in ['.mp4']:
                        resultado['problemas'].append("Recomendado usar formato MP4 para melhor compatibilidade")
                
                break
        
        if not categoria_encontrada:
            resultado['problemas'].append(f"Formato não suportado: {extensao} ({mime_type})")
        
        # Arquivo é válido se não há problemas
        resultado['valido'] = len(resultado['problemas']) == 0
        
        return resultado
    
    def listar_formatos_suportados(self) -> None:
        """Lista todos os formatos suportados"""
        print("📋 FORMATOS DE MÍDIA SUPORTADOS PELO WHATSAPP")
        print("=" * 50)
        
        for categoria, info in self.formatos_suportados.items():
            print(f"\n📁 {categoria.upper()}")
            print(f"   Endpoint: {info['endpoint']}")
            print(f"   Limite: {info['limite_mb']}MB")
            print(f"   Extensões: {', '.join(info['extensoes'])}")
            print(f"   MIME Types: {', '.join(info['tipos'])}")
            if 'observacoes' in info:
                print(f"   ⚠️ {info['observacoes']}")
    
    def testar_arquivo(self, caminho_arquivo: str, numero_destino: str = None) -> Dict:
        """Testa um arquivo específico"""
        print(f"\n🧪 TESTANDO ARQUIVO: {os.path.basename(caminho_arquivo)}")
        print("-" * 40)
        
        # Verificar formato
        info_arquivo = self.verificar_formato_arquivo(caminho_arquivo)
        
        print(f"📄 Nome: {info_arquivo['nome']}")
        print(f"📏 Tamanho: {info_arquivo['tamanho_mb']} MB")
        print(f"🏷️ Tipo MIME: {info_arquivo['mime_type']}")
        print(f"📂 Categoria: {info_arquivo['categoria']}")
        print(f"🎯 Endpoint: {info_arquivo['endpoint']}")
        
        if info_arquivo['problemas']:
            print("\n⚠️ PROBLEMAS ENCONTRADOS:")
            for problema in info_arquivo['problemas']:
                print(f"   • {problema}")
        
        if info_arquivo['valido']:
            print("✅ Formato válido para envio")
            
            # Testar envio se número fornecido
            if numero_destino:
                print(f"\n📤 Testando envio para {numero_destino}...")
                resultado_envio = self._enviar_arquivo(caminho_arquivo, numero_destino, info_arquivo)
                info_arquivo['resultado_envio'] = resultado_envio
                
                if resultado_envio['sucesso']:
                    print("✅ Envio realizado com sucesso!")
                else:
                    print(f"❌ Falha no envio: {resultado_envio['erro']}")
        else:
            print("❌ Formato inválido para envio")
        
        return info_arquivo
    
    def _enviar_arquivo(self, caminho_arquivo: str, numero_destino: str, info_arquivo: Dict) -> Dict:
        """Envia arquivo via WAHA"""
        try:
            url = f"{self.base_url}{info_arquivo['endpoint']}"
            
            # Preparar número (formato WhatsApp)
            numero_limpo = numero_destino.replace('+', '').replace('-', '').replace(' ', '')
            chat_id = f"{numero_limpo}@c.us"
            
            with open(caminho_arquivo, 'rb') as file:
                files = {'file': file}
                data = {
                    'chatId': chat_id,
                    'caption': f'Teste de formato: {info_arquivo["categoria"]} - {datetime.now().strftime("%H:%M:%S")}',
                    'session': self.instance_id
                }
                
                headers = self.headers.copy()
                if 'Content-Type' in headers:
                    del headers['Content-Type']
                
                response = requests.post(url, files=files, data=data, 
                                       headers=headers, timeout=60)
                
                if response.status_code in [200, 201]:
                    try:
                        result = response.json()
                        if response.status_code == 201 or result.get('success', False):
                            return {
                                'sucesso': True,
                                'status_code': response.status_code,
                                'resposta': result
                            }
                        else:
                            return {
                                'sucesso': False,
                                'status_code': response.status_code,
                                'erro': result.get('message', 'Erro desconhecido'),
                                'resposta': result
                            }
                    except json.JSONDecodeError:
                        return {
                            'sucesso': False,
                            'status_code': response.status_code,
                            'erro': 'Resposta inválida do servidor',
                            'resposta': response.text[:200]
                        }
                else:
                    try:
                        error_detail = response.json()
                        return {
                            'sucesso': False,
                            'status_code': response.status_code,
                            'erro': error_detail.get('message', f'Erro HTTP {response.status_code}'),
                            'resposta': error_detail
                        }
                    except:
                        return {
                            'sucesso': False,
                            'status_code': response.status_code,
                            'erro': f'Erro HTTP {response.status_code}',
                            'resposta': response.text[:200]
                        }
                        
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f'Exceção durante envio: {str(e)}'
            }
    
    def testar_diretorio(self, caminho_diretorio: str, numero_destino: str = None) -> Dict:
        """Testa todos os arquivos de um diretório"""
        if not os.path.isdir(caminho_diretorio):
            print(f"❌ Diretório não encontrado: {caminho_diretorio}")
            return {}
        
        print(f"\n📁 TESTANDO DIRETÓRIO: {caminho_diretorio}")
        print("=" * 50)
        
        resultados = {
            'total_arquivos': 0,
            'arquivos_validos': 0,
            'arquivos_invalidos': 0,
            'envios_sucesso': 0,
            'envios_falha': 0,
            'detalhes': []
        }
        
        # Listar arquivos
        arquivos = [f for f in os.listdir(caminho_diretorio) 
                   if os.path.isfile(os.path.join(caminho_diretorio, f))]
        
        resultados['total_arquivos'] = len(arquivos)
        
        for arquivo in arquivos:
            caminho_completo = os.path.join(caminho_diretorio, arquivo)
            resultado_arquivo = self.testar_arquivo(caminho_completo, numero_destino)
            
            resultados['detalhes'].append(resultado_arquivo)
            
            if resultado_arquivo['valido']:
                resultados['arquivos_validos'] += 1
                
                if 'resultado_envio' in resultado_arquivo:
                    if resultado_arquivo['resultado_envio']['sucesso']:
                        resultados['envios_sucesso'] += 1
                    else:
                        resultados['envios_falha'] += 1
            else:
                resultados['arquivos_invalidos'] += 1
            
            # Pausa entre envios para evitar rate limiting
            if numero_destino:
                time.sleep(2)
        
        # Resumo
        print(f"\n📊 RESUMO DO TESTE")
        print("-" * 30)
        print(f"Total de arquivos: {resultados['total_arquivos']}")
        print(f"Arquivos válidos: {resultados['arquivos_validos']}")
        print(f"Arquivos inválidos: {resultados['arquivos_invalidos']}")
        
        if numero_destino:
            print(f"Envios bem-sucedidos: {resultados['envios_sucesso']}")
            print(f"Envios falharam: {resultados['envios_falha']}")
        
        return resultados
    
    def gerar_relatorio_detalhado(self, resultados: Dict, salvar_arquivo: bool = True) -> None:
        """Gera relatório detalhado dos testes"""
        relatorio = {
            'timestamp': datetime.now().isoformat(),
            'resumo': {
                'total_arquivos': resultados.get('total_arquivos', 0),
                'arquivos_validos': resultados.get('arquivos_validos', 0),
                'arquivos_invalidos': resultados.get('arquivos_invalidos', 0),
                'envios_sucesso': resultados.get('envios_sucesso', 0),
                'envios_falha': resultados.get('envios_falha', 0)
            },
            'detalhes_por_categoria': {},
            'problemas_comuns': [],
            'recomendacoes': []
        }
        
        # Agrupar por categoria
        for detalhe in resultados.get('detalhes', []):
            categoria = detalhe.get('categoria', 'desconhecido')
            if categoria not in relatorio['detalhes_por_categoria']:
                relatorio['detalhes_por_categoria'][categoria] = {
                    'total': 0,
                    'validos': 0,
                    'invalidos': 0,
                    'arquivos': []
                }
            
            cat_info = relatorio['detalhes_por_categoria'][categoria]
            cat_info['total'] += 1
            cat_info['arquivos'].append(detalhe)
            
            if detalhe['valido']:
                cat_info['validos'] += 1
            else:
                cat_info['invalidos'] += 1
                relatorio['problemas_comuns'].extend(detalhe['problemas'])
        
        # Gerar recomendações
        if relatorio['resumo']['arquivos_invalidos'] > 0:
            relatorio['recomendacoes'].append("Converter arquivos inválidos para formatos suportados")
        
        if relatorio['resumo']['envios_falha'] > 0:
            relatorio['recomendacoes'].append("Verificar configuração do WAHA e status da sessão")
        
        relatorio['recomendacoes'].extend([
            "Usar MP4 para vídeos (codec H.264)",
            "Manter arquivos abaixo do limite de tamanho",
            "Testar com arquivos pequenos primeiro",
            "Verificar logs do WAHA em caso de falhas"
        ])
        
        if salvar_arquivo:
            filename = f"relatorio_formatos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(relatorio, f, indent=2, ensure_ascii=False)
                print(f"\n💾 Relatório salvo em: {filename}")
            except Exception as e:
                print(f"\n❌ Erro ao salvar relatório: {e}")
        
        return relatorio
    
    def criar_arquivos_teste(self, diretorio_destino: str = "arquivos_teste") -> None:
        """Cria arquivos de teste para diferentes formatos"""
        print(f"\n🔧 Criando arquivos de teste em: {diretorio_destino}")
        
        os.makedirs(diretorio_destino, exist_ok=True)
        
        # Criar arquivo de texto simples
        with open(os.path.join(diretorio_destino, "teste.txt"), 'w', encoding='utf-8') as f:
            f.write("Arquivo de teste para WAHA\n")
            f.write(f"Criado em: {datetime.now()}\n")
        
        print("✅ Arquivo teste.txt criado")
        print(f"📁 Adicione outros arquivos de teste em: {diretorio_destino}")
        print("   Sugestões: imagem.jpg, video.mp4, audio.mp3, documento.pdf")

def main():
    """Função principal"""
    print("🧪 Teste de Formatos de Mídia - WAHA")
    print("=" * 40)
    
    if len(sys.argv) < 2:
        print("\n📖 USO:")
        print("  python teste_formatos_midia.py --formatos                    # Listar formatos suportados")
        print("  python teste_formatos_midia.py arquivo.jpg [numero]          # Testar arquivo específico")
        print("  python teste_formatos_midia.py --dir pasta [numero]          # Testar diretório")
        print("  python teste_formatos_midia.py --criar-teste                 # Criar arquivos de teste")
        print("\n📝 Exemplos:")
        print("  python teste_formatos_midia.py imagem.jpg +5511999999999")
        print("  python teste_formatos_midia.py --dir uploads +5511999999999")
        return
    
    tester = TesteFormatosMidia()
    
    comando = sys.argv[1]
    
    if comando == "--formatos":
        tester.listar_formatos_suportados()
    
    elif comando == "--criar-teste":
        diretorio = sys.argv[2] if len(sys.argv) > 2 else "arquivos_teste"
        tester.criar_arquivos_teste(diretorio)
    
    elif comando == "--dir":
        if len(sys.argv) < 3:
            print("❌ Especifique o diretório")
            return
        
        diretorio = sys.argv[2]
        numero = sys.argv[3] if len(sys.argv) > 3 else None
        
        resultados = tester.testar_diretorio(diretorio, numero)
        tester.gerar_relatorio_detalhado(resultados)
    
    else:
        # Testar arquivo específico
        arquivo = comando
        numero = sys.argv[2] if len(sys.argv) > 2 else None
        
        if not os.path.exists(arquivo):
            print(f"❌ Arquivo não encontrado: {arquivo}")
            return
        
        resultado = tester.testar_arquivo(arquivo, numero)
        
        # Salvar resultado individual
        filename = f"teste_{os.path.basename(arquivo)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Resultado salvo em: {filename}")
        except Exception as e:
            print(f"\n❌ Erro ao salvar resultado: {e}")

if __name__ == "__main__":
    main()