# Despliegue Persistente - Aplicación de Visualización de Primos

Este documento describe cómo desplegar y gestionar la aplicación de visualización de primos con persistencia utilizando systemd.

## Archivos Importantes

- `deploy_enhanced.py`: Script principal de la aplicación Flask
- `index_interactive_enhanced.html`: Interfaz de usuario HTML
- `prime-visualization.service`: Archivo de configuración del servicio systemd
- `deploy_persistent.sh`: Script para instalar y configurar el servicio
- `manage_app.sh`: Script para gestionar fácilmente la aplicación
- `enhanced_app.log`: Archivo de logs de la aplicación

## Instrucciones de Despliegue

### Método 1: Usando el script de despliegue

1. Ejecute el script de despliegue con privilegios de administrador:
   ```
   sudo bash deploy_persistent.sh
   ```

2. El script realizará las siguientes acciones:
   - Verificar que todos los archivos necesarios existen
   - Instalar el servicio systemd
   - Configurar el inicio automático
   - Iniciar el servicio
   - Mostrar el estado actual

### Método 2: Instalación manual

Si prefiere realizar la instalación manualmente:

1. Copie el archivo de servicio al directorio de systemd:
   ```
   sudo cp prime-visualization.service /etc/systemd/system/
   ```

2. Recargue la configuración de systemd:
   ```
   sudo systemctl daemon-reload
   ```

3. Habilite el servicio para que se inicie automáticamente:
   ```
   sudo systemctl enable prime-visualization.service
   ```

4. Inicie el servicio:
   ```
   sudo systemctl start prime-visualization.service
   ```

5. Verifique el estado:
   ```
   sudo systemctl status prime-visualization.service
   ```

## Gestión de la Aplicación

### Usando el script de gestión

El script `manage_app.sh` proporciona una interfaz sencilla para gestionar la aplicación:

- **Iniciar**: `./manage_app.sh start`
- **Detener**: `./manage_app.sh stop`
- **Reiniciar**: `./manage_app.sh restart`
- **Estado**: `./manage_app.sh status`
- **Ver logs**: `./manage_app.sh logs`
- **Ver logs en tiempo real**: `./manage_app.sh logs-live`
- **Ejecutar despliegue**: `./manage_app.sh deploy`
- **Ayuda**: `./manage_app.sh help`

### Usando systemctl directamente

También puede gestionar el servicio directamente con systemctl:

- **Iniciar**: `sudo systemctl start prime-visualization.service`
- **Detener**: `sudo systemctl stop prime-visualization.service`
- **Reiniciar**: `sudo systemctl restart prime-visualization.service`
- **Estado**: `sudo systemctl status prime-visualization.service`
- **Ver logs**: `sudo journalctl -u prime-visualization.service`

## Acceso a la Aplicación

Una vez desplegada, la aplicación estará disponible en:

- **URL principal**: http://localhost:3000
- **Interfaz mejorada**: http://localhost:3000/enhanced
- **API de información**: http://localhost:3000/api/info

## Solución de Problemas

Si la aplicación no se inicia correctamente:

1. Verifique los logs:
   ```
   tail -n 50 /home/admin/enhanced_app.log
   ```

2. Verifique el estado del servicio:
   ```
   sudo systemctl status prime-visualization.service
   ```

3. Asegúrese de que el puerto 3000 no esté siendo utilizado por otra aplicación:
   ```
   sudo lsof -i :3000
   ```

4. Reinicie el servicio:
   ```
   sudo systemctl restart prime-visualization.service
   ```

## Desinstalación

Si necesita desinstalar el servicio:

1. Detenga el servicio:
   ```
   sudo systemctl stop prime-visualization.service
   ```

2. Deshabilite el inicio automático:
   ```
   sudo systemctl disable prime-visualization.service
   ```

3. Elimine el archivo de servicio:
   ```
   sudo rm /etc/systemd/system/prime-visualization.service
   ```

4. Recargue la configuración de systemd:
   ```
   sudo systemctl daemon-reload
   ```