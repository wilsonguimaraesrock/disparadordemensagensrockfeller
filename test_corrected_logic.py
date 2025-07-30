#!/usr/bin/env python3
"""
Script para testar a lógica corrigida de envio de mensagens
"""

import requests
import json
import time
import pandas as pd
import os
from pathlib import Path

def test_corrected_sending():
    """Testar o envio corrigido via API"""
    
    base_url = "http://127.0.0.1:5001"
    
    print("🧪 TESTE DA LÓGICA CORRIGIDA")
    print("=" * 50)
    
    # 1. Verificar se o sistema está funcionando
    try:
        response = requests.get(f"{base_url}/api/get_config")
        if response.status_code == 200:
            config = response.json()
            print(f"✅ Sistema funcionando - Config carregada")
        else:
            print(f"❌ Erro ao verificar sistema: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return
    
    # 2. Configurar sequência de teste
    sequence_data = {
        "sequence": [
            {
                "type": "text",
                "content": "Primeira mensagem de teste para {nome}"
            },
            {
                "type": "text", 
                "content": "Segunda mensagem de teste para {nome}"
            },
            {
                "type": "text",
                "content": "Terceira mensagem de teste para {nome}"
            }
        ],
        "interval": 3,  # 3 segundos entre mensagens
        "fallback_name": "amigo(a)"
    }
    
    try:
        response = requests.post(f"{base_url}/api/save_message", json=sequence_data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Sequência configurada")
            else:
                print(f"❌ Erro ao configurar sequência: {result.get('error')}")
                return
        else:
            print(f"❌ Erro ao configurar sequência: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Erro ao configurar sequência: {e}")
        return
    
    # 3. Configurar contatos de teste (criar arquivo Excel temporário)
    contacts_data = [
        {"numero": "+5547996322763", "nome": "Teste 1"},
        {"numero": "+5547996322764", "nome": "Teste 2"},
        {"numero": "+5547996322765", "nome": "Teste 3"}
    ]
    
    # Criar arquivo Excel temporário
    temp_file = "test_contacts_temp.xlsx"
    try:
        df = pd.DataFrame(contacts_data)
        df.to_excel(temp_file, index=False)
        
        # Enviar arquivo via upload
        with open(temp_file, 'rb') as f:
            files = {'file': (temp_file, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(f"{base_url}/api/upload_contacts", files=files)
            
        if response.status_code == 200:
            print("✅ Contatos configurados")
        else:
            print(f"❌ Erro ao configurar contatos: {response.status_code}")
            if response.text:
                print(f"Detalhes: {response.text}")
            return
    except Exception as e:
        print(f"❌ Erro ao configurar contatos: {e}")
        return
    finally:
        # Remover arquivo temporário
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    # 4. Validar contatos
    print("\n🔍 Validando contatos...")
    try:
        response = requests.post(f"{base_url}/api/validate_contacts", json={})
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                stats = result.get('stats', {})
                print(f"✅ Contatos validados: {stats.get('valid', 0)} válidos, {stats.get('invalid', 0)} inválidos")
            else:
                print(f"❌ Erro na validação: {result.get('error')}")
                return
        else:
            print(f"❌ Erro ao validar contatos: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Erro ao validar contatos: {e}")
        return
    
    # 5. Iniciar envio
    print("\n🚀 Iniciando teste de envio...")
    print("📊 Esperado: 3 contatos × 3 mensagens = 9 mensagens total")
    print("⏱️ Com intervalos entre mensagens e entre contatos")
    print("\n📝 Acompanhe os logs em tempo real...")
    
    try:
        response = requests.post(f"{base_url}/api/start_sending", json={})
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Envio iniciado com sucesso!")
                print("\n📋 Monitorando progresso...")
                
                # Monitorar progresso
                for i in range(60):  # Monitorar por até 60 segundos
                    time.sleep(2)
                    try:
                        progress_response = requests.get(f"{base_url}/api/contacts_preview")
                        if progress_response.status_code == 200:
                            progress = progress_response.json()
                            stats = progress.get('stats', {})
                            current = stats.get('sent', 0)
                            total = stats.get('loaded', 0)
                            success = stats.get('success', 0)
                            error = stats.get('error', 0)
                            
                            print(f"\r📊 Progresso: {current}/{total} | ✅ {success} | ❌ {error}", end="")
                            
                            if current >= total and total > 0:
                                print("\n\n🎉 TESTE CONCLUÍDO!")
                                print(f"📈 Resultado final: {success} sucessos, {error} erros")
                                break
                    except:
                        continue
                
            else:
                print(f"❌ Erro no envio: {result.get('error')}")
        else:
            print(f"❌ Erro ao iniciar envio: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao iniciar envio: {e}")
    
    print("\n" + "=" * 50)
    print("🔍 Verifique os logs detalhados na interface web")
    print("🌐 Acesse: http://127.0.0.1:5001")

if __name__ == "__main__":
    test_corrected_sending()