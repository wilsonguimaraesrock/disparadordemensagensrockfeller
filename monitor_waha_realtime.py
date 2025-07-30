#!/usr/bin/env python3
"""
Monitor em Tempo Real do WAHA
Monitora continuamente o status do WAHA e detecta problemas automaticamente
"""

import os
import sys
import json
import time
import signal
import requests
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import deque

class MonitorWAHA:
    def __init__(self, config_path: str = "config.json"):
        self.config = self._carregar_config(config_path)
        self.base_url = self.config.get('base_url', 'http://localhost:3000')
        self.token = self.config.get('token', '')
        self.instance_id = self.config.get('instance_id', 'default')
        self.headers = {'X-API-KEY': self.token}
        
        # Configurações de monitoramento
        self.intervalo_verificacao = 30  # segundos
        self.timeout_request = 10  # segundos
        self.max_tentativas_reconexao = 3
        self.historico_status = deque(maxlen=100)  # Últimos 100 status
        
        # Estado do monitor
        self.rodando = False
        self.thread_monitor = None
        self.ultimo_status = None
        self.problemas_detectados = []
        self.alertas_enviados = set()
        
        # Métricas
        self.metricas = {
            'uptime_inicio': None,
            'total_verificacoes': 0,
            'verificacoes_sucesso': 0,
            'verificacoes_falha': 0,
            'tempo_inatividade_total': 0,
            'ultima_inatividade_inicio': None,
            'reconexoes_automaticas': 0
        }
        
        # Configurar handler para interrupção
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _carregar_config(self, config_path: str) -> Dict:
        """Carrega configurações do arquivo JSON"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Arquivo de configuração não encontrado: {config_path}")
            return {}
        except json.JSONDecodeError:
            print(f"❌ Erro ao decodificar JSON: {config_path}")
            return {}
    
    def _signal_handler(self, signum, frame):
        """Handler para sinais de interrupção"""
        print(f"\n🛑 Recebido sinal {signum}. Parando monitor...")
        self.parar_monitor()
        sys.exit(0)
    
    def _log_com_timestamp(self, mensagem: str, nivel: str = "INFO") -> None:
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        simbolo = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "DEBUG": "🔍"
        }.get(nivel, "📝")
        
        print(f"[{timestamp}] {simbolo} {mensagem}")
        
        # Salvar em arquivo de log
        try:
            with open("monitor_waha.log", "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] [{nivel}] {mensagem}\n")
        except Exception:
            pass  # Ignorar erros de log
    
    def verificar_status_waha(self) -> Dict:
        """Verifica o status atual do WAHA"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'waha_online': False,
            'sessao_ativa': False,
            'token_valido': False,
            'tempo_resposta': None,
            'status_sessao': 'UNKNOWN',
            'problemas': [],
            'detalhes': {}
        }
        
        inicio_verificacao = time.time()
        
        try:
            # 1. Verificar se WAHA está online
            response = requests.get(f"{self.base_url}/api/health", 
                                  timeout=self.timeout_request)
            
            tempo_resposta = time.time() - inicio_verificacao
            status['tempo_resposta'] = round(tempo_resposta, 3)
            
            if response.status_code == 200:
                status['waha_online'] = True
                
                # 2. Verificar token
                try:
                    sessions_response = requests.get(f"{self.base_url}/api/sessions", 
                                                    headers=self.headers, 
                                                    timeout=self.timeout_request)
                    if sessions_response.status_code == 200:
                        status['token_valido'] = True
                        
                        # 3. Verificar sessão específica
                        session_response = requests.get(
                            f"{self.base_url}/api/sessions/{self.instance_id}", 
                            headers=self.headers, 
                            timeout=self.timeout_request
                        )
                        
                        if session_response.status_code == 200:
                            session_data = session_response.json()
                            status['status_sessao'] = session_data.get('status', 'UNKNOWN')
                            status['detalhes']['sessao'] = session_data
                            
                            if status['status_sessao'] == 'WORKING':
                                status['sessao_ativa'] = True
                            elif status['status_sessao'] == 'SCAN_QR_CODE':
                                status['problemas'].append('Sessão aguardando QR Code')
                            elif status['status_sessao'] == 'FAILED':
                                status['problemas'].append('Sessão falhou')
                        else:
                            status['problemas'].append(f'Erro ao verificar sessão: {session_response.status_code}')
                    
                    elif sessions_response.status_code == 401:
                        status['problemas'].append('Token de API inválido')
                    else:
                        status['problemas'].append(f'Erro de autenticação: {sessions_response.status_code}')
                        
                except Exception as e:
                    status['problemas'].append(f'Erro ao verificar token/sessão: {str(e)}')
            else:
                status['problemas'].append(f'WAHA respondeu com status {response.status_code}')
                
        except requests.exceptions.ConnectionError:
            status['problemas'].append('WAHA não está acessível')
        except requests.exceptions.Timeout:
            status['problemas'].append('Timeout ao conectar com WAHA')
        except Exception as e:
            status['problemas'].append(f'Erro inesperado: {str(e)}')
        
        return status
    
    def detectar_problemas(self, status_atual: Dict) -> List[str]:
        """Detecta problemas baseado no status atual e histórico"""
        problemas = []
        
        # Problemas diretos do status
        problemas.extend(status_atual['problemas'])
        
        # Análise de tempo de resposta
        if status_atual['tempo_resposta'] and status_atual['tempo_resposta'] > 5:
            problemas.append(f"Tempo de resposta alto: {status_atual['tempo_resposta']}s")
        
        # Análise de histórico
        if len(self.historico_status) >= 3:
            ultimos_3 = list(self.historico_status)[-3:]
            
            # Verificar instabilidade
            status_diferentes = len(set(s['status_sessao'] for s in ultimos_3))
            if status_diferentes > 1:
                problemas.append("Instabilidade detectada na sessão")
            
            # Verificar falhas consecutivas
            falhas_consecutivas = sum(1 for s in ultimos_3 if not s['waha_online'])
            if falhas_consecutivas >= 2:
                problemas.append(f"Falhas consecutivas detectadas: {falhas_consecutivas}")
        
        return problemas
    
    def tentar_correcao_automatica(self, problemas: List[str]) -> List[str]:
        """Tenta corrigir problemas automaticamente"""
        correcoes_aplicadas = []
        
        for problema in problemas:
            if "Sessão falhou" in problema:
                self._log_com_timestamp("Tentando reiniciar sessão automaticamente...", "WARNING")
                if self._reiniciar_sessao():
                    correcoes_aplicadas.append("Sessão reiniciada com sucesso")
                    self.metricas['reconexoes_automaticas'] += 1
                else:
                    self._log_com_timestamp("Falha ao reiniciar sessão automaticamente", "ERROR")
            
            elif "WAHA não está acessível" in problema:
                self._log_com_timestamp("Tentando reconectar ao WAHA...", "WARNING")
                time.sleep(5)  # Aguardar antes de tentar novamente
        
        return correcoes_aplicadas
    
    def _reiniciar_sessao(self) -> bool:
        """Reinicia a sessão WAHA"""
        try:
            # Parar sessão atual
            stop_url = f"{self.base_url}/api/sessions/{self.instance_id}/stop"
            requests.post(stop_url, headers=self.headers, timeout=self.timeout_request)
            
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
            self._log_com_timestamp(f"Erro ao reiniciar sessão: {e}", "ERROR")
            return False
    
    def _loop_monitoramento(self) -> None:
        """Loop principal de monitoramento"""
        self._log_com_timestamp("Monitor iniciado", "SUCCESS")
        self.metricas['uptime_inicio'] = datetime.now()
        
        while self.rodando:
            try:
                # Verificar status
                status = self.verificar_status_waha()
                self.historico_status.append(status)
                self.ultimo_status = status
                
                # Atualizar métricas
                self.metricas['total_verificacoes'] += 1
                
                if status['waha_online'] and status['sessao_ativa']:
                    self.metricas['verificacoes_sucesso'] += 1
                    
                    # Se estava inativo, calcular tempo de inatividade
                    if self.metricas['ultima_inatividade_inicio']:
                        tempo_inativo = datetime.now() - self.metricas['ultima_inatividade_inicio']
                        self.metricas['tempo_inatividade_total'] += tempo_inativo.total_seconds()
                        self.metricas['ultima_inatividade_inicio'] = None
                        
                        self._log_com_timestamp(
                            f"Sistema voltou ao normal após {tempo_inativo.total_seconds():.1f}s de inatividade", 
                            "SUCCESS"
                        )
                else:
                    self.metricas['verificacoes_falha'] += 1
                    
                    # Marcar início de inatividade
                    if not self.metricas['ultima_inatividade_inicio']:
                        self.metricas['ultima_inatividade_inicio'] = datetime.now()
                
                # Detectar problemas
                problemas = self.detectar_problemas(status)
                
                if problemas:
                    # Log apenas novos problemas
                    novos_problemas = [p for p in problemas if p not in self.alertas_enviados]
                    
                    for problema in novos_problemas:
                        self._log_com_timestamp(f"Problema detectado: {problema}", "WARNING")
                        self.alertas_enviados.add(problema)
                    
                    # Tentar correção automática
                    if novos_problemas:
                        correcoes = self.tentar_correcao_automatica(novos_problemas)
                        for correcao in correcoes:
                            self._log_com_timestamp(f"Correção aplicada: {correcao}", "SUCCESS")
                else:
                    # Limpar alertas se não há problemas
                    if self.alertas_enviados:
                        self._log_com_timestamp("Todos os problemas foram resolvidos", "SUCCESS")
                        self.alertas_enviados.clear()
                
                # Log periódico de status (a cada 10 verificações)
                if self.metricas['total_verificacoes'] % 10 == 0:
                    self._log_status_periodico(status)
                
                # Aguardar próxima verificação
                time.sleep(self.intervalo_verificacao)
                
            except Exception as e:
                self._log_com_timestamp(f"Erro no loop de monitoramento: {e}", "ERROR")
                time.sleep(self.intervalo_verificacao)
    
    def _log_status_periodico(self, status: Dict) -> None:
        """Log periódico do status"""
        uptime = datetime.now() - self.metricas['uptime_inicio']
        taxa_sucesso = (self.metricas['verificacoes_sucesso'] / 
                       self.metricas['total_verificacoes'] * 100) if self.metricas['total_verificacoes'] > 0 else 0
        
        self._log_com_timestamp(
            f"Status: WAHA={'ON' if status['waha_online'] else 'OFF'} | "
            f"Sessão={status['status_sessao']} | "
            f"Uptime={uptime.total_seconds():.0f}s | "
            f"Taxa sucesso={taxa_sucesso:.1f}% | "
            f"Verificações={self.metricas['total_verificacoes']}",
            "INFO"
        )
    
    def iniciar_monitor(self) -> None:
        """Inicia o monitoramento"""
        if self.rodando:
            self._log_com_timestamp("Monitor já está rodando", "WARNING")
            return
        
        self.rodando = True
        self.thread_monitor = threading.Thread(target=self._loop_monitoramento, daemon=True)
        self.thread_monitor.start()
        
        self._log_com_timestamp(f"Monitor iniciado - Verificando a cada {self.intervalo_verificacao}s", "SUCCESS")
    
    def parar_monitor(self) -> None:
        """Para o monitoramento"""
        if not self.rodando:
            return
        
        self.rodando = False
        
        if self.thread_monitor and self.thread_monitor.is_alive():
            self.thread_monitor.join(timeout=5)
        
        self._log_com_timestamp("Monitor parado", "INFO")
        self._gerar_relatorio_final()
    
    def _gerar_relatorio_final(self) -> None:
        """Gera relatório final do monitoramento"""
        if not self.metricas['uptime_inicio']:
            return
        
        uptime_total = datetime.now() - self.metricas['uptime_inicio']
        
        # Calcular tempo de inatividade final
        if self.metricas['ultima_inatividade_inicio']:
            tempo_inativo_atual = datetime.now() - self.metricas['ultima_inatividade_inicio']
            self.metricas['tempo_inatividade_total'] += tempo_inativo_atual.total_seconds()
        
        taxa_sucesso = (self.metricas['verificacoes_sucesso'] / 
                       self.metricas['total_verificacoes'] * 100) if self.metricas['total_verificacoes'] > 0 else 0
        
        disponibilidade = ((uptime_total.total_seconds() - self.metricas['tempo_inatividade_total']) / 
                          uptime_total.total_seconds() * 100) if uptime_total.total_seconds() > 0 else 0
        
        relatorio = {
            'periodo_monitoramento': {
                'inicio': self.metricas['uptime_inicio'].isoformat(),
                'fim': datetime.now().isoformat(),
                'duracao_segundos': uptime_total.total_seconds()
            },
            'estatisticas': {
                'total_verificacoes': self.metricas['total_verificacoes'],
                'verificacoes_sucesso': self.metricas['verificacoes_sucesso'],
                'verificacoes_falha': self.metricas['verificacoes_falha'],
                'taxa_sucesso_percent': round(taxa_sucesso, 2),
                'disponibilidade_percent': round(disponibilidade, 2),
                'tempo_inatividade_total_segundos': self.metricas['tempo_inatividade_total'],
                'reconexoes_automaticas': self.metricas['reconexoes_automaticas']
            },
            'ultimo_status': self.ultimo_status,
            'historico_recente': list(self.historico_status)[-10:]  # Últimos 10 status
        }
        
        # Salvar relatório
        filename = f"relatorio_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(relatorio, f, indent=2, ensure_ascii=False)
            
            self._log_com_timestamp(f"Relatório final salvo em: {filename}", "SUCCESS")
        except Exception as e:
            self._log_com_timestamp(f"Erro ao salvar relatório: {e}", "ERROR")
        
        # Log do resumo
        print("\n" + "=" * 50)
        print("📊 RESUMO DO MONITORAMENTO")
        print("=" * 50)
        print(f"⏱️ Duração: {uptime_total.total_seconds():.0f}s")
        print(f"🔍 Verificações: {self.metricas['total_verificacoes']}")
        print(f"✅ Taxa de sucesso: {taxa_sucesso:.1f}%")
        print(f"📈 Disponibilidade: {disponibilidade:.1f}%")
        print(f"⚠️ Tempo inativo: {self.metricas['tempo_inatividade_total']:.0f}s")
        print(f"🔄 Reconexões automáticas: {self.metricas['reconexoes_automaticas']}")
        print("=" * 50)
    
    def status_atual(self) -> Dict:
        """Retorna o status atual"""
        return self.ultimo_status or {}
    
    def configurar_intervalo(self, segundos: int) -> None:
        """Configura o intervalo de verificação"""
        if segundos < 5:
            segundos = 5
        self.intervalo_verificacao = segundos
        self._log_com_timestamp(f"Intervalo de verificação alterado para {segundos}s", "INFO")

def main():
    """Função principal"""
    print("🔍 Monitor em Tempo Real do WAHA")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("\n📖 USO:")
            print("  python monitor_waha_realtime.py                    # Iniciar monitor")
            print("  python monitor_waha_realtime.py --intervalo 60     # Monitor com intervalo de 60s")
            print("  python monitor_waha_realtime.py --status           # Verificar status uma vez")
            print("\n⌨️ Durante o monitoramento:")
            print("  Ctrl+C para parar o monitor")
            return
        
        elif sys.argv[1] == "--status":
            monitor = MonitorWAHA()
            status = monitor.verificar_status_waha()
            print(json.dumps(status, indent=2, ensure_ascii=False))
            return
    
    # Verificar se arquivo de configuração existe
    if not os.path.exists('config.json'):
        print("❌ Arquivo config.json não encontrado!")
        print("💡 Crie o arquivo config.json com as configurações do WAHA")
        return
    
    # Inicializar monitor
    monitor = MonitorWAHA()
    
    # Configurar intervalo se especificado
    if len(sys.argv) > 2 and sys.argv[1] == "--intervalo":
        try:
            intervalo = int(sys.argv[2])
            monitor.configurar_intervalo(intervalo)
        except ValueError:
            print("❌ Intervalo deve ser um número")
            return
    
    # Verificação inicial
    print("🔍 Verificação inicial...")
    status_inicial = monitor.verificar_status_waha()
    
    if not status_inicial['waha_online']:
        print("❌ WAHA não está acessível. Verifique se está rodando.")
        resposta = input("Continuar monitoramento mesmo assim? (s/N): ")
        if resposta.lower() != 's':
            return
    
    # Iniciar monitoramento
    monitor.iniciar_monitor()
    
    try:
        print("\n🔍 Monitoramento ativo. Pressione Ctrl+C para parar.")
        print("📊 Logs sendo salvos em: monitor_waha.log")
        
        # Manter programa rodando
        while monitor.rodando:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n🛑 Interrompido pelo usuário")
    
    finally:
        monitor.parar_monitor()

if __name__ == "__main__":
    main()