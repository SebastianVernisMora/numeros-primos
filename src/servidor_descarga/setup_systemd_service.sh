#!/bin/bash

echo "🔧 CONFIGURANDO SERVICIO SYSTEMD PARA SERVIDOR UNIFICADO..."
echo "=========================================================="

# Detener servidor actual
echo "🛑 Deteniendo servidor actual..."
pkill -f static_app || true
sleep 2

# Crear archivo de servicio systemd
echo "📝 Creando archivo de servicio..."
sudo tee /etc/systemd/system/mapas-primos.service > /dev/null << EOF
[Unit]
Description=Servidor Unificado de Mapas de Números Primos
After=network.target

[Service]
Type=simple
User=admin
WorkingDirectory=/home/admin/servidor_descarga
ExecStart=/usr/bin/python3 -O /home/admin/servidor_descarga/unified_server.py --port=3000 --host=0.0.0.0
Restart=always
RestartSec=10
StandardOutput=append:/home/admin/servidor_descarga/systemd_unified.log
StandardError=append:/home/admin/servidor_descarga/systemd_unified_error.log

# Variables de entorno
Environment=PYTHONUNBUFFERED=1
Environment=PYTHONPATH=/home/admin/servidor_descarga

# Recursos y límites
LimitNOFILE=65536
MemoryAccounting=yes
MemoryMax=2G

# Reinicio automático en caso de falla
StartLimitIntervalSec=300
StartLimitBurst=10

[Install]
WantedBy=multi-user.target
EOF

# Recargar systemd
echo "🔄 Recargando systemd..."
sudo systemctl daemon-reload

# Habilitar servicio para inicio automático
echo "⚙️ Habilitando servicio..."
sudo systemctl enable mapas-primos.service

# Iniciar servicio
echo "🚀 Iniciando servicio..."
sudo systemctl start mapas-primos.service

# Esperar inicialización
echo "⏳ Esperando inicialización..."
sleep 5

# Verificar estado
echo "🔍 Verificando estado del servicio..."
if sudo systemctl is-active mapas-primos.service > /dev/null; then
    echo ""
    echo "🔥 SERVICIO SYSTEMD CONFIGURADO CON ÉXITO"
    echo "========================================"
    echo ""
    echo "📊 ESTADO DEL SERVICIO:"
    sudo systemctl status mapas-primos.service --no-pager -l
    echo ""
    echo "🌐 ACCESOS PÚBLICOS:"
    echo "   📍 http://3.144.134.110:3000/ (selector)"
    echo "   🗺️ http://3.144.134.110:3000/interactive"
    echo "   🎨 http://3.144.134.110:3000/images"
    echo ""
    echo "🛠️ GESTIÓN DEL SERVICIO:"
    echo "   Iniciar:    sudo systemctl start mapas-primos"
    echo "   Detener:    sudo systemctl stop mapas-primos"
    echo "   Reiniciar:  sudo systemctl restart mapas-primos"
    echo "   Estado:     sudo systemctl status mapas-primos"
    echo "   Logs:       sudo journalctl -u mapas-primos -f"
    echo "   Logs app:   tail -f systemd_unified.log"
    echo ""
    echo "⚡ CARACTERÍSTICAS:"
    echo "   • Reinicio automático en crasheos"
    echo "   • Inicio automático del sistema"
    echo "   • Límite de memoria: 2GB"
    echo "   • Límite de archivos: 65536"
    echo "   • Logs persistentes"
    echo "   • Límites de reinicio para evitar loops"
    echo ""
    echo "✅ SERVICIO ACTIVO Y MONITOREADO POR SYSTEMD"
else
    echo "❌ ERROR: El servicio no se pudo iniciar"
    echo "📋 Logs de error:"
    sudo journalctl -u mapas-primos.service --no-pager -n 20
fi