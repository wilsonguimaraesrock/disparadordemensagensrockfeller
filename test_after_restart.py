#!/usr/bin/env python3
import requests
import time
import json

print('Testando WAHA após reinicialização...')

headers = {
    'X-Api-Key': 'waha-key-2025',
    'Content-Type': 'application/json'
}

# Criar sessão
print('1. Criando sessão default...')
r = requests.post('http://localhost:3000/api/sessions', 
                 headers=headers, 
                 json={'name': 'default'})
print(f'Create Status: {r.status_code}')
print(f'Create Response: {r.text}')

time.sleep(2)

# Iniciar sessão
print('\n2. Iniciando sessão...')
r2 = requests.post('http://localhost:3000/api/sessions/default/start', 
                  headers=headers)
print(f'Start Status: {r2.status_code}')
print(f'Start Response: {r2.text}')

time.sleep(3)

# Verificar status
print('\n3. Verificando status...')
r3 = requests.get('http://localhost:3000/api/sessions/default', 
                 headers=headers)
print(f'Status Check: {r3.status_code}')
if r3.status_code == 200:
    session_data = r3.json()
    print(f'Session Data: {json.dumps(session_data, indent=2)}')
else:
    print(f'Error Response: {r3.text}')

# Listar todas as sessões
print('\n4. Listando todas as sessões...')
r4 = requests.get('http://localhost:3000/api/sessions', headers=headers)
print(f'List Status: {r4.status_code}')
print(f'Sessions: {r4.text}')