#!/usr/bin/env python3
"""
Script para monitorar a conexão da sessão WAHA em tempo real
"""

import requests
import time
import json
from datetime import datetime

def monitor_waha_connection():
    """Monitora a conexão WAHA em tempo real"""
    
    # Configurações WAHA
    base_url = "http://localhost:3000"
    api_key = "waha-key-2025"
    session_name = "default"
    
    print("📡 Monitor de Conexão WAHA")
    print("=" * 40)
    print("📱 QR Code disponível em: http://127.0.0.1:5000/qr_waha")
    print("⏹️  Pressione Ctrl+C para parar o monitor")
    print("=" * 40)
    
    last_status = None
    check_count = 0
    
    try:
        while True:
            check_count += 1
            current_time = datetime.now().strftime("%H:%M:%S")
            
            try:
                # Verificar status da sessão
                url = f"{base_url}/api/sessions/{session_name}"
                headers = {'X-Api-Key': api_key}
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    current_status = data.get('status', 'UNKNOWN')
                    
                    # Só mostrar se o status mudou ou a cada 10 verificações
                    if current_status != last_status or check_count % 10 == 0:
                        print(f"\n[{current_time}] 📊 Status: {current_status}")
                        
                        if current_status == 'WORKING':
                            me = data.get('me')
                            if me:
                                user_name = me.get('pushname', 'N/A')
                                user_id = me.get('id', 'N/A')
                                print(f"✅ CONECTADO! Usuário: {user_name} ({user_id})")
                                print("🎉 WhatsApp está pronto para enviar mensagens!")
                                
                                # Testar envio de mensagem
                                test_connection(base_url, api_key, session_name, user_id)
                                break
                            else:
                                print("✅ CONECTADO! (dados do usuário não disponíveis)")
                                break
                                
                        elif current_status == 'STARTING':
                            if current_status != last_status:
                                print("⏳ Aguardando escaneamento do QR code...")
                                
                        elif current_status == 'STOPPED':
                            print("⛔ Sessão parada - execute restart_waha_session.py")
                            break
                            
                        elif current_status == 'FAILED':
                            print("❌ Sessão falhou - execute restart_waha_session.py")
                            break
                            
                        last_status = current_status
                    
                    # Mostrar progresso a cada verificação
                    if check_count % 10 != 0:
                        print(".", end="", flush=True)
                        
                else:
                    print(f"\n[{current_time}] ❌ Erro HTTP: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"\n[{current_time}] ❌ Erro de conexão: {e}")
            except Exception as e:
                print(f"\n[{current_time}] ❌ Erro: {e}")
            
            # Aguardar 3 segundos antes da próxima verificação
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Monitor interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro no monitor: {e}")
    
    print("\n🏁 Monitor finalizado")

def test_connection(base_url, api_key, session_name, user_id):
    """Testa a conexão enviando uma mensagem para si mesmo"""
    print("\n🧪 Testando conexão...")
    
    try:
        url = f"{base_url}/api/sendText"
        payload = {
            "chatId": user_id,
            "text": "✅ Teste de conexão WAHA - Sistema funcionando!",
            "session": session_name
        }
        
        headers = {
            'X-Api-Key': api_key,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code in [200, 201]:
            print("✅ Teste de envio bem-sucedido!")
            print("📱 Verifique seu WhatsApp para confirmar o recebimento")
        else:
            print(f"⚠️ Teste falhou: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Erro: {error_data}")
            except:
                print(f"   Resposta: {response.text}")
                
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

if __name__ == "__main__":
    monitor_waha_connection()