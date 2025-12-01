#!/bin/bash

# Script para desplegar la aplicación de visualización de primos con persistencia
# Este script configura un servicio systemd para que la aplicación se ejecute
# automáticamente al iniciar el sistema y se reinicie en caso de fallos

echo "🚀 Iniciando despliegue persistente de la aplicación de visualización de primos..."

# Verificar si el script se ejecuta como root
if [ "$EUID" -ne 0 ]; then
  echo "⚠️ Este script debe ejecutarse con privilegios de administrador (sudo)"
  echo "Por favor, ejecute: sudo bash deploy_persistent.sh"
  exit 1
fi

# Verificar que el archivo de servicio existe
if [ ! -f "/home/admin/prime-visualization.service" ]; then
  echo "❌ Error: No se encuentra el archivo prime-visualization.service"
  exit 1
fi

# Verificar que el script de la aplicación existe
if [ ! -f "/home/admin/deploy_enhanced.py" ]; then
  echo "❌ Error: No se encuentra el archivo deploy_enhanced.py"
  exit 1
fi

# Asegurar que el script tiene permisos de ejecución
chmod +x /home/admin/deploy_enhanced.py

# Copiar el archivo de servicio a systemd
echo "📋 Instalando servicio systemd..."
cp /home/admin/prime-visualization.service /etc/systemd/system/

# Recargar la configuración de systemd
echo "🔄 Recargando configuración de systemd..."
systemctl daemon-reload

# Habilitar el servicio para que se inicie automáticamente
echo "✅ Habilitando inicio automático del servicio..."
systemctl enable prime-visualization.service

# Detener el servicio si ya está en ejecución
if systemctl is-active --quiet prime-visualization.service; then
  echo "🛑 Deteniendo servicio existente..."
  systemctl stop prime-visualization.service
fi

# Iniciar el servicio
echo "▶️ Iniciando servicio..."
systemctl start prime-visualization.service

# Verificar el estado del servicio
echo "🔍 Verificando estado del servicio..."
systemctl status prime-visualization.service

echo ""
echo "✨ Despliegue completado ✨"
echo "La aplicación ahora está configurada para ejecutarse persistentemente"
echo "y reiniciarse automáticamente en caso de fallos o reinicios del sistema."
echo ""
echo "📊 Acceda a la aplicación en: http://localhost:3000"
echo "📝 Logs disponibles en: /home/admin/enhanced_app.log"
echo "⚙️ Gestione el servicio con: sudo systemctl [start|stop|restart|status] prime-visualization.service"