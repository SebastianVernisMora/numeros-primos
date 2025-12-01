#!/bin/bash
# Script para ver logs del generador PM2 en tiempo real

echo "📋 Logs del Generador de Datos PM2"
echo "===================================="
echo ""
echo "Presiona Ctrl+C para salir"
echo ""

pm2 logs prime-map-generator --lines 100
