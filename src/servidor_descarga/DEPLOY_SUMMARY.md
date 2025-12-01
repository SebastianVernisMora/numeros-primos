# 🚀 SERVIDOR UNIFICADO DE MAPAS DE NÚMEROS PRIMOS

## ✅ ESTADO ACTUAL: DESPLEGADO Y ACTIVO

### 🌐 URLS PÚBLICAS DISPONIBLES

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Selector** | `http://3.144.134.110:3000/` | Página principal con selector de servicios |
| **Interactivo** | `http://3.144.134.110:3000/interactive` | Mapa interactivo con zoom, drag, tooltips |
| **Imágenes** | `http://3.144.134.110:3000/images` | Generador de imágenes PNG optimizado |
| **Proxy** | `http://3.144.134.110/` | Acceso a través de Apache (puerto 80) |

### 🎯 FUNCIONALIDADES

#### 🗺️ MAPA INTERACTIVO
- **Visualización en tiempo real** de números primos
- **Zoom y navegación** (rueda del mouse + drag)
- **Tooltips informativos** al hacer hover
- **Clasificación completa** de tipos de primos:
  - Primos regulares, gemelos, primos, sexy
  - Sophie Germain, palíndromos, Mersenne, Fermat
- **Múltiples mapeos geométricos**
- **Sin números compuestos** para mejor rendimiento

#### 🎨 GENERADOR DE IMÁGENES
- **Límites ampliados:** Hasta **10,000 círculos**
- **Generación PNG optimizada** (solo números primos)
- **Leyenda automática** con colores explicativos  
- **Parámetros en encabezado** de la imagen
- **Múltiples resoluciones:** 150, 300, 600 DPI
- **Descarga automática** con nombres descriptivos
- **Advertencias** para números grandes (>100K elementos)

### ⚙️ CONFIGURACIÓN DEL SERVICIO

#### 🔧 SYSTEMD SERVICE: `mapas-primos.service`
- **Reinicio automático** en caso de crashes
- **Inicio automático** del sistema
- **Límite de memoria:** 2GB
- **Monitoreo continuo** por systemd
- **Logs persistentes**

#### 📋 COMANDOS DE GESTIÓN
```bash
# Control básico
./control_service.sh {start|stop|restart|status|logs|test}

# Comandos systemd directos
sudo systemctl start mapas-primos     # Iniciar
sudo systemctl stop mapas-primos      # Detener  
sudo systemctl restart mapas-primos   # Reiniciar
sudo systemctl status mapas-primos    # Estado
sudo journalctl -u mapas-primos -f    # Logs en vivo
```

### 📊 APIS DISPONIBLES

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/info` | GET | Información general del sistema |
| `/api/interactive-map` | POST | Generar datos para mapa interactivo |
| `/api/number/{n}` | GET | Información detallada de un número |
| `/api/generate-image` | POST | Generar y descargar imagen PNG |

### 🚀 OPTIMIZACIONES IMPLEMENTADAS

- **Sin números compuestos:** Reducción 80% de elementos
- **Procesamiento por chunks** para números grandes
- **Gestión automática de memoria** 
- **Validaciones de seguridad** para evitar sobrecarga
- **Limpieza automática** de archivos temporales
- **Reinicio resiliente** con systemd

### ✅ SERVICIO LISTO PARA PRODUCCIÓN

El servidor está completamente configurado y monitoreado, listo para manejar cargas de trabajo pesadas con reinicio automático en caso de problemas.