#!/bin/bash
# Script para detener el servidor

echo "🛑 Deteniendo servicios..."

# Detener servicios systemd si están activos
if systemctl is-active --quiet servidor_descarga.service; then
    echo "🔄 Deteniendo servicio principal..."
    sudo systemctl stop servidor_descarga.service
    echo "✅ Servicio principal detenido"
else
    echo "ℹ️ Servicio principal no está activo"
fi

if systemctl is-active --quiet autodeploy.service; then
    echo "🔄 Deteniendo servicio de auto-deploy..."
    sudo systemctl stop autodeploy.service
    echo "✅ Servicio de auto-deploy detenido"
else
    echo "ℹ️ Servicio de auto-deploy no está activo"
fi

# Detener procesos manualmente por si acaso
echo "🔍 Buscando procesos activos..."
pkill -f "python.*static_app.py" 2>/dev/null || true
pkill -f "python.*auto_deploy.py" 2>/dev/null || true

# Verificar puerto 3000
if ss -tlnp | grep -q :3000; then
    echo "⚠️ Puerto 3000 aún en uso, liberando..."
    fuser -k 3000/tcp 2>/dev/null || true
    sleep 2
fi

# Verificar puerto 9000
if ss -tlnp | grep -q :9000; then
    echo "⚠️ Puerto 9000 aún en uso, liberando..."
    fuser -k 9000/tcp 2>/dev/null || true
    sleep 2
fi

echo "✅ Todos los servicios detenidos"