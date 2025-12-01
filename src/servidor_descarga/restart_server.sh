#!/bin/bash
# Script para reiniciar el servidor

echo "🔄 Reiniciando servicios..."

# Detener servicios
echo "🛑 Deteniendo servicios actuales..."
./stop_server.sh

# Esperar un momento
sleep 2

# Reiniciar servicios systemd
echo "🚀 Iniciando servicios..."

if systemctl list-unit-files | grep -q servidor_descarga.service; then
    echo "🔄 Reiniciando servicio principal..."
    sudo systemctl restart servidor_descarga.service
    echo "✅ Servicio principal reiniciado"
else
    echo "⚠️ Servicio principal no está instalado, ejecutando script de despliegue..."
    ./deploy_public_port3000.sh
fi

if systemctl list-unit-files | grep -q autodeploy.service; then
    echo "🔄 Reiniciando servicio de auto-deploy..."
    sudo systemctl restart autodeploy.service
    echo "✅ Servicio de auto-deploy reiniciado"
else
    echo "⚠️ Servicio de auto-deploy no está instalado"
    echo "💡 Ejecuta ./setup_dns_persistence.sh para configurar los servicios"
fi

# Verificar estado
echo "🔍 Verificando estado de los servicios..."
sleep 5

# Verificar puerto 3000
if ss -tlnp | grep -q :3000; then
    echo "✅ Servidor principal activo en puerto 3000"
else
    echo "❌ Servidor principal no está activo"
fi

# Verificar puerto 9000
if ss -tlnp | grep -q :9000; then
    echo "✅ Servidor de auto-deploy activo en puerto 9000"
else
    echo "❌ Servidor de auto-deploy no está activo"
fi

# Obtener información de red
LOCAL_IP=$(hostname -I | awk '{print $1}')
HOSTNAME=$(hostname -f)

echo ""
echo "🌐 ACCESOS DISPONIBLES:"
echo "   📍 IP PÚBLICA:   http://${LOCAL_IP}:3000/"
echo "   🌍 DNS/HOSTNAME: http://${HOSTNAME}:3000/"
echo "   🔗 LOCALHOST:    http://localhost:3000/"