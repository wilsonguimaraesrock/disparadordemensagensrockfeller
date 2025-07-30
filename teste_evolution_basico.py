#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste básico da Evolution API
Verifica conectividade e endpoints disponíveis
"""

import requests
import json
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:8080"
API_KEY = "evolution-api-key-2025"
INSTANCE_NAME = "whatsapp-sender-v2"

headers = {
    'apikey': API_KEY,
    'Content-Type': 'application/json'
}

def testar_endpoint(method, endpoint, data=None):
    """Testa um endpoint específico"""
    try:
        url = f"{BASE_URL}{endpoint}"
        print(f"\n🔍 Testando {method} {endpoint}")
        
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=10)
        else:
            print(f"   ❌ Método {method} não suportado")
            return None
            
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   ✅ Sucesso: {json.dumps(result, indent=2)[:200]}...")
                return result
            except:
                print(f"   ✅ Sucesso: {response.text[:200]}...")
                return response.text
        else:
            print(f"   ❌ Erro: {response.text[:200]}...")
            return None
            
    except requests.exceptions.Timeout:
        print(f"   ⏰ Timeout na requisição")
        return None
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
        return None

def main():
    print("🧪 TESTE BÁSICO - EVOLUTION API")
    print("="*50)
    
    # Lista de endpoints para testar
    endpoints = [
        ('GET', '/'),
        ('GET', '/instance/fetchInstances'),
        ('GET', f'/instance/{INSTANCE_NAME}'),
        ('GET', f'/instance/connectionState/{INSTANCE_NAME}'),
        ('POST', f'/instance/restart/{INSTANCE_NAME}'),
        ('GET', f'/instance/qr/{INSTANCE_NAME}'),
        ('POST', f'/instance/logout/{INSTANCE_NAME}'),
    ]
    
    resultados = []
    
    for method, endpoint in endpoints:
        resultado = testar_endpoint(method, endpoint)
        resultados.append({
            'method': method,
            'endpoint': endpoint,
            'sucesso': resultado is not None,
            'resultado': str(resultado)[:100] if resultado else None
        })
    
    # Relatório final
    print("\n" + "="*50)
    print("📊 RELATÓRIO FINAL")
    print("="*50)
    
    sucessos = sum(1 for r in resultados if r['sucesso'])
    print(f"\nResumo: {sucessos}/{len(resultados)} endpoints funcionando")
    
    print("\n📋 Detalhes:")
    for r in resultados:
        status = "✅" if r['sucesso'] else "❌"
        print(f"  {status} {r['method']} {r['endpoint']}")
    
    # Salvar relatório
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"teste_evolution_basico_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'base_url': BASE_URL,
            'instance_name': INSTANCE_NAME,
            'resultados': resultados,
            'resumo': {
                'total_endpoints': len(resultados),
                'sucessos': sucessos,
                'falhas': len(resultados) - sucessos
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Relatório salvo em: {filename}")
    
    if sucessos > 0:
        print("\n✅ Evolution API está respondendo!")
        print("Para conectar ao WhatsApp:")
        print("1. Acesse http://localhost:8080")
        print("2. Encontre sua instância")
        print("3. Escaneie o QR Code")
    else:
        print("\n❌ Evolution API não está respondendo corretamente")
        print("Verifique se o Docker está rodando")

if __name__ == "__main__":
    main()