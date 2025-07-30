#!/usr/bin/env python3
import requests
import time
import json

headers = {'X-Api-Key': 'waha-key-2025'}

print('Monitorando status da sessão WAHA...')
print('=' * 40)

for i in range(10):
    try:
        response = requests.get('http://localhost:3000/api/sessions/default', headers=headers)
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'UNKNOWN')
            print(f'Tentativa {i+1}: Status = {status}')
            
            if status == 'SCAN_QR':
                print('\n🎉 QR CODE PRONTO!')
                print('Acesse: http://localhost:3000/dashboard')
                print('Clique na sessão "default" para ver o QR code')
                break
            elif status == 'WORKING':
                print('\n✅ SESSÃO CONECTADA!')
                print('WhatsApp já está conectado!')
                break
            elif status == 'FAILED':
                print('\n❌ SESSÃO FALHOU')
                break
        else:
            print(f'Tentativa {i+1}: Erro {response.status_code}')
    except Exception as e:
        print(f'Tentativa {i+1}: Erro - {e}')
    
    if i < 9:
        time.sleep(5)

print('\nMonitoramento concluído.')