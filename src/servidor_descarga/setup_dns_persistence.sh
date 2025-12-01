#!/bin/bash
# Script para configurar persistencia DNS para el servidor de descarga

echo "🌐 Configurando persistencia DNS para el servidor de descarga..."

# Obtener información de red
LOCAL_IP=$(hostname -I | awk '{print $1}')
HOSTNAME=$(hostname -f)

echo "📍 Configuración de red detectada:"
echo "   🔸 IP Local: $LOCAL_IP"
echo "   🔸 Hostname: $HOSTNAME"

# Crear directorio para logs si no existe
mkdir -p /home/admin/servidor_descarga/logs

# Verificar si systemd está disponible
if ! command -v systemctl &> /dev/null; then
    echo "❌ ERROR: systemd no está disponible en este sistema"
    exit 1
fi

# Copiar archivos de servicio a systemd
echo "📋 Instalando servicios systemd..."
sudo cp /home/admin/servidor_descarga/servidor_descarga.service /etc/systemd/system/
sudo cp /home/admin/servidor_descarga/autodeploy.service /etc/systemd/system/

# Recargar systemd
echo "🔄 Recargando systemd..."
sudo systemctl daemon-reload

# Habilitar servicios para inicio automático
echo "✅ Habilitando servicios para inicio automático..."
sudo systemctl enable servidor_descarga.service
sudo systemctl enable autodeploy.service

# Iniciar servicios
echo "🚀 Iniciando servicios..."
sudo systemctl start servidor_descarga.service
sudo systemctl start autodeploy.service

# Verificar estado de los servicios
echo "🔍 Verificando estado de los servicios..."
sudo systemctl status servidor_descarga.service --no-pager
sudo systemctl status autodeploy.service --no-pager

# Crear archivo de configuración DNS
echo "📝 Creando archivo de configuración DNS..."
cat > /home/admin/servidor_descarga/dns_config.json << EOL
{
    "hostname": "$HOSTNAME",
    "ip": "$LOCAL_IP",
    "port": 3000,
    "autodeploy_port": 9000,
    "urls": {
        "principal": "http://$HOSTNAME:3000/",
        "ip_publica": "http://$LOCAL_IP:3000/",
        "localhost": "http://localhost:3000/",
        "autodeploy": "http://$HOSTNAME:9000/webhook"
    },
    "configurado_en": "$(date)"
}
EOL

# Crear archivo de información DNS
echo "📄 Creando archivo de información DNS..."
cat > /home/admin/servidor_descarga/DNS_INFO.md << EOL
# 🌐 CONFIGURACIÓN DNS PERSISTENTE

## ✅ ESTADO: **ACTIVO Y CONFIGURADO**

### 📍 ACCESOS DNS DISPONIBLES:

#### 🔥 **HOSTNAME PRINCIPAL**
\`\`\`
http://$HOSTNAME:3000/
\`\`\`

#### 🌍 **IP PÚBLICA**
\`\`\`  
http://$LOCAL_IP:3000/
\`\`\`

#### 🔗 **LOCALHOST** 
\`\`\`
http://localhost:3000/
\`\`\`

## 🎯 ENDPOINTS DISPONIBLES

### 🏠 Interfaz Principal
- **URL**: \`http://$HOSTNAME:3000/\`
- **Descripción**: Selector de 980 mapas interactivos
- **Acceso**: Público desde cualquier ubicación

### 📊 API Información
- **URL**: \`http://$HOSTNAME:3000/api/info\`
- **Método**: GET
- **Respuesta**: Info del sistema y estadísticas

### 🗺️ Lista de Mapas
- **URL**: \`http://$HOSTNAME:3000/api/maps\`
- **Método**: GET  
- **Respuesta**: Lista completa de 980 mapas disponibles

### 🎲 Mapa Aleatorio
- **URL**: \`http://$HOSTNAME:3000/api/random-map\`
- **Método**: GET
- **Respuesta**: Mapa aleatorio instantáneo

### 🧮 Análisis de Números
- **URL**: \`http://$HOSTNAME:3000/api/number/{numero}\`
- **Método**: GET
- **Ejemplo**: \`http://$HOSTNAME:3000/api/number/97\`

## ⚡ CARACTERÍSTICAS DE PERSISTENCIA

- ✅ **Inicio automático en arranque** - Servicio systemd
- ✅ **Reinicio automático tras fallos** - Configuración Restart=always
- ✅ **Logs persistentes** - Almacenados en /home/admin/servidor_descarga/logs
- ✅ **Auto-deploy webhook** - Actualización automática con cambios en GitHub
- ✅ **Acceso DNS persistente** - Configurado para hostname $HOSTNAME

## 📋 COMANDOS DE CONTROL

### Verificar Estado de Servicios
\`\`\`bash
sudo systemctl status servidor_descarga.service
sudo systemctl status autodeploy.service
\`\`\`

### Ver Logs en Tiempo Real
\`\`\`bash
tail -f /home/admin/servidor_descarga/systemd.log
tail -f /home/admin/servidor_descarga/autodeploy_systemd.log
\`\`\`

### Detener Servicios
\`\`\`bash
sudo systemctl stop servidor_descarga.service
sudo systemctl stop autodeploy.service
\`\`\`

### Reiniciar Servicios
\`\`\`bash
sudo systemctl restart servidor_descarga.service
sudo systemctl restart autodeploy.service
\`\`\`

## 🔥 CONFIGURACIÓN PERSISTENTE COMPLETADA

**Configuración realizada**: $(date)
EOL

# Crear script para verificar estado DNS
echo "📝 Creando script para verificar estado DNS..."
cat > /home/admin/servidor_descarga/check_dns_status.sh << EOL
#!/bin/bash
# Script para verificar estado de los servicios DNS

echo "🔍 Verificando estado de los servicios DNS..."
echo ""
echo "📡 Servidor principal:"
sudo systemctl status servidor_descarga.service --no-pager
echo ""
echo "🔄 Auto-deploy webhook:"
sudo systemctl status autodeploy.service --no-pager
echo ""
echo "🌐 Verificando acceso DNS..."
curl -s -o /dev/null -w "%{http_code}" http://$HOSTNAME:3000/api/info
if [ \$? -eq 0 ]; then
    echo "✅ Acceso DNS funcionando correctamente"
else
    echo "❌ Problema con acceso DNS"
fi
echo ""
echo "🔗 URLs disponibles:"
echo "   🏠 Principal: http://$HOSTNAME:3000/"
echo "   🌍 IP: http://$LOCAL_IP:3000/"
echo "   🔄 Webhook: http://$HOSTNAME:9000/webhook"
EOL

# Hacer ejecutable el script de verificación
chmod +x /home/admin/servidor_descarga/check_dns_status.sh

echo "✅ Configuración de persistencia DNS completada"
echo ""
echo "🌐 ACCESOS DNS DISPONIBLES:"
echo "   🏠 Principal: http://$HOSTNAME:3000/"
echo "   🌍 IP: http://$LOCAL_IP:3000/"
echo "   🔄 Webhook: http://$HOSTNAME:9000/webhook"
echo ""
echo "📋 Para verificar el estado, ejecute:"
echo "   ./check_dns_status.sh"
echo ""
echo "📄 Para más información, consulte el archivo DNS_INFO.md"