#!/usr/bin/env python3
import requests
import json

def test_proxy_routes():
    """Testa as rotas de proxy WAHA na aplicação Flask"""
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testando rotas de proxy WAHA...")
    print("=" * 50)
    
    # Teste 1: Verificar status da sessão
    print("\n1. Testando /api/waha/session/status/default")
    try:
        response = requests.get(f"{base_url}/api/waha/session/status/default")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ Status da sessão: {data.get('status')}")
            else:
                print(f"   ❌ Erro: {data.get('error')}")
        else:
            print(f"   ❌ Erro HTTP: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exceção: {e}")
    
    # Teste 2: Verificar QR code
    print("\n2. Testando /api/waha/qr/default")
    try:
        response = requests.get(f"{base_url}/api/waha/qr/default")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ QR code disponível: {len(data.get('qr_code', ''))} caracteres")
            else:
                print(f"   ❌ Erro: {data.get('error')}")
        else:
            print(f"   ❌ Erro HTTP: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Exceção: {e}")
    
    # Teste 3: Comparar com API direta do WAHA
    print("\n3. Comparando com API direta do WAHA")
    try:
        response = requests.get(
            "http://localhost:3000/api/sessions/default",
            headers={'X-Api-Key': 'waha-key-2025'}
        )
        print(f"   Status direto WAHA: {response.status_code}")
        print(f"   Response direto: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status direto: {data.get('status')}")
    except Exception as e:
        print(f"   ❌ Exceção: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Teste concluído!")

if __name__ == '__main__':
    test_proxy_routes()