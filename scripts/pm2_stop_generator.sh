#!/bin/bash
# Script para detener el generador de datos PM2

echo "🛑 Deteniendo Generador de Datos PM2..."

pm2 stop prime-map-generator
pm2 delete prime-map-generator

echo "✅ Generador detenido y eliminado de PM2"
echo ""
echo "📊 Estado actual de PM2:"
pm2 list
