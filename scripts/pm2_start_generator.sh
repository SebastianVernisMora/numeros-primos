#!/bin/bash
# Script para iniciar el generador de datos con PM2

echo "🚀 Iniciando Generador de Datos con PM2..."

# Crear directorio de logs si no existe
mkdir -p logs

# Iniciar con PM2
pm2 start ecosystem.config.js

# Mostrar estado
echo ""
echo "📊 Estado del generador:"
pm2 list

echo ""
echo "✅ Generador iniciado!"
echo "📋 Ver logs: pm2 logs prime-map-generator"
echo "📊 Ver estado: ./scripts/pm2_status_generator.sh"
echo "🛑 Detener: ./scripts/pm2_stop_generator.sh"
