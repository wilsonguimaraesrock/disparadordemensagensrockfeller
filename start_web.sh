#!/bin/bash

# WhatsApp API Sender - Web Server Launcher for Linux/Mac

echo ""
echo "========================================================="
echo "   WhatsApp API Sender - Interface Web"
echo "========================================================="
echo ""

# Ir para o diretório do script
cd "$(dirname "$0")"

# Executar servidor Python
python3 run_server.py

echo ""
echo "Pressione Enter para fechar..."
read 