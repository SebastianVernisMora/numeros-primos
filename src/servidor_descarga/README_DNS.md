# 🌐 Despliegue con Persistencia DNS

Este proyecto incluye un sistema completo para desplegar el servidor de mapas interactivos con persistencia DNS, asegurando que el servicio esté siempre disponible y accesible a través de DNS e IP.

## 📋 Características Principales

- ✅ **Persistencia total** - El servidor se inicia automáticamente al arrancar el sistema
- ✅ **Acceso DNS persistente** - Configuración para acceso por hostname
- ✅ **Auto-recuperación** - Reinicio automático en caso de fallos
- ✅ **Auto-deploy** - Webhook para actualización automática desde GitHub
- ✅ **Monitorización** - Scripts para verificar el estado del servicio

## 🚀 Instalación y Configuración

Para configurar el sistema con persistencia DNS, ejecute:

```bash
./setup_dns_persistence.sh
```

Este script realizará las siguientes acciones:
1. Crear servicios systemd para el servidor principal y el webhook de auto-deploy
2. Configurar el inicio automático de los servicios
3. Iniciar los servicios
4. Crear archivos de configuración DNS
5. Generar documentación con las URLs de acceso

## 🛠️ Comandos Principales

### Iniciar Servicios
```bash
sudo systemctl start servidor_descarga.service
sudo systemctl start autodeploy.service
```

### Detener Servicios
```bash
./stop_server.sh
```
o
```bash
sudo systemctl stop servidor_descarga.service
sudo systemctl stop autodeploy.service
```

### Reiniciar Servicios
```bash
./restart_server.sh
```
o
```bash
sudo systemctl restart servidor_descarga.service
sudo systemctl restart autodeploy.service
```

### Verificar Estado
```bash
./check_dns_status.sh
```
o
```bash
sudo systemctl status servidor_descarga.service
sudo systemctl status autodeploy.service
```

## 🌐 Acceso al Servidor

Una vez configurado, el servidor estará disponible en:

- **DNS/Hostname**: `http://<hostname>:3000/`
- **IP Pública**: `http://<ip>:3000/`
- **Localhost**: `http://localhost:3000/`

## 📊 Endpoints Principales

- **Interfaz Principal**: `http://<hostname>:3000/`
- **API Info**: `http://<hostname>:3000/api/info`
- **Lista de Mapas**: `http://<hostname>:3000/api/maps`
- **Mapa Aleatorio**: `http://<hostname>:3000/api/random-map`
- **Análisis de Números**: `http://<hostname>:3000/api/number/<numero>`
- **Verificación DNS**: `http://<hostname>:3000/dns-check`

## 🔄 Auto-Deploy Webhook

El sistema incluye un webhook para despliegue automático desde GitHub:

- **URL del Webhook**: `http://<hostname>:9000/webhook`
- **Endpoint Manual**: `http://<hostname>:9000/manual-deploy`
- **Verificación de Estado**: `http://<hostname>:9000/status`

## 📝 Logs del Sistema

Los logs del sistema se almacenan en:

- **Servidor Principal**: `/home/admin/servidor_descarga/systemd.log`
- **Auto-Deploy**: `/home/admin/servidor_descarga/autodeploy_systemd.log`
- **Errores del Servidor**: `/home/admin/servidor_descarga/systemd_error.log`
- **Errores de Auto-Deploy**: `/home/admin/servidor_descarga/autodeploy_systemd_error.log`

## ⚠️ Solución de Problemas

Si el servidor no responde:

1. Verificar estado de los servicios: `./check_dns_status.sh`
2. Reiniciar servicios: `./restart_server.sh`
3. Verificar logs: `tail -f /home/admin/servidor_descarga/systemd.log`
4. Comprobar puertos: `ss -tlnp | grep 3000`