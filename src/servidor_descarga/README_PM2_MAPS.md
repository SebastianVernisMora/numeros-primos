# 🗺️ Sistema de Generación de Mapas con PM2

Sistema automatizado para generar y servir mapas de números primos con soporte para hasta **10,000 círculos × 1,300 segmentos** (13 millones de elementos).

## 📋 Características

- ✅ Generación en segundo plano con PM2
- ✅ Soporte hasta 10,000 círculos × 1,300 segmentos
- ✅ Datos pregenerados y almacenados localmente
- ✅ Servidor web optimizado para servir datos
- ✅ Monitoreo y estadísticas en tiempo real
- ✅ Reinicio automático y gestión de recursos

## 🚀 Instalación Rápida

### 1. Instalar PM2 (si no está instalado)

```bash
npm install -g pm2
```

### 2. Instalar dependencias de Python

```bash
pip install flask flask-cors
```

### 3. Dar permisos de ejecución

```bash
chmod +x pm2_manager.sh
chmod +x static_maps_server.py
chmod +x background_map_generator.py
```

## 🎯 Uso del Gestor PM2

El script `pm2_manager.sh` es la herramienta principal para controlar el generador.

### Comandos Disponibles

```bash
# Iniciar el generador de mapas
./pm2_manager.sh start

# Ver estado actual
./pm2_manager.sh status

# Ver logs en tiempo real
./pm2_manager.sh logs

# Ver estadísticas detalladas
./pm2_manager.sh stats

# Monitor interactivo de PM2
./pm2_manager.sh monitor

# Reiniciar el proceso
./pm2_manager.sh restart

# Detener el generador
./pm2_manager.sh stop

# Eliminar el proceso de PM2
./pm2_manager.sh delete

# Limpiar logs antiguos
./pm2_manager.sh clean

# Mostrar ayuda
./pm2_manager.sh help
```

## 📊 Proceso de Generación

### Rangos Configurados

El generador crea mapas con las siguientes configuraciones:

| Rango | Círculos | Segmentos | Elementos Máx |
|-------|----------|-----------|---------------|
| Básico | 5 - 50 | 12 - 60 | 3,000 |
| Medio | 60 - 200 | 60 - 180 | 36,000 |
| Alto | 250 - 500 | 180 - 300 | 150,000 |
| Súper Denso | 600 - 1,000 | 300 - 360 | 360,000 |
| Ultra Denso | 1,000 - 3,000 | 360 - 500 | 1,500,000 |
| **Mega Denso** | 3,000 - 5,000 | 500 - 800 | 4,000,000 |
| **Extremo** | 5,000 - 10,000 | 800 - 1,300 | **13,000,000** |

### Optimizaciones para Mapas Grandes

El sistema aplica optimizaciones automáticas según el tamaño del mapa:

- **< 100k elementos**: Sin optimización (todos los puntos)
- **100k - 500k**: Máximo 50k puntos renderizados
- **500k - 1M**: Máximo 30k puntos renderizados
- **1M - 5M**: Máximo 25k puntos renderizados
- **> 5M elementos**: Máximo 15k puntos renderizados

Esto garantiza que incluso mapas de 13M elementos sean manejables en el frontend.

## 🌐 Servidor Web

### Iniciar el servidor

```bash
python3 static_maps_server.py
```

El servidor estará disponible en: `http://localhost:3000`

### API Endpoints

#### 1. Listar todos los mapas
```bash
GET /api/maps
```

Respuesta:
```json
{
  "success": true,
  "total": 1523,
  "maps": [
    {
      "hash": "abc123def456",
      "parametros": {
        "num_circulos": 10000,
        "divisiones_por_circulo": 1300,
        "tipo_mapeo": "lineal"
      },
      "elementos_count": 15000,
      "primos_count": 1230
    }
  ]
}
```

#### 2. Obtener mapa por hash
```bash
GET /api/map/{hash}
```

#### 3. Obtener mapa por parámetros
```bash
POST /api/get-map
Content-Type: application/json

{
  "num_circulos": 10000,
  "divisiones_por_circulo": 1300,
  "tipo_mapeo": "lineal",
  "filtros": {
    "primos": true,
    "compuestos": true
  }
}
```

#### 4. Estadísticas del servidor
```bash
GET /api/stats
```

#### 5. Health check
```bash
GET /health
```

## 📈 Monitoreo

### Ver progreso de generación

```bash
# Ver logs en tiempo real
./pm2_manager.sh logs

# Ver estadísticas
./pm2_manager.sh stats

# Monitor interactivo
./pm2_manager.sh monitor
```

### Archivos de estadísticas

El generador mantiene estadísticas en:
- `background_generator_stats.json` - Estadísticas en tiempo real
- `logs/` - Logs del proceso PM2
- `static_maps/index.json` - Índice de mapas generados

### Ejemplo de estadísticas

```json
{
  "started_at": "2025-12-01T10:30:00",
  "maps_generated": 1523,
  "errors": 3,
  "current_task": "Generando 8000×1200 [extremo]",
  "last_activity": "2025-12-01T12:45:32",
  "total_size_mb": 2345.67
}
```

## 🔧 Configuración Avanzada

### Modificar límites de generación

Editar `background_map_generator.py`:

```python
# Línea 92-93: Modificar rangos máximos
circulos_extremo = list(range(5000, 15001, 1000))  # Hasta 15,000 círculos
segmentos_extremo = list(range(800, 2001, 100))    # Hasta 2,000 segmentos
```

### Configuración de PM2

Editar `ecosystem.config.js`:

```javascript
{
  max_memory_restart: '8G',  // Aumentar límite de memoria
  cron_restart: '0 3 * * *', // Reiniciar a las 3 AM diariamente
}
```

### Habilitar compresión en servidor

En `static_maps_server.py`:

```python
COMPRESSION_ENABLED = True  # Comprimir respuestas con gzip
```

## 📂 Estructura de Archivos

```
servidor_descarga/
├── background_map_generator.py  # Generador principal
├── static_maps_server.py        # Servidor web
├── pm2_manager.sh               # Script de gestión
├── ecosystem.config.js          # Configuración PM2
├── static_maps/                 # Mapas generados
│   ├── data_*.json             # Datos de mapas
│   └── index.json              # Índice de mapas
├── logs/                        # Logs de PM2
│   ├── map-generator-out.log
│   ├── map-generator-error.log
│   └── background_generator_*.log
└── background_generator_stats.json
```

## 🎨 Integración con Frontend

### Ejemplo de uso en HTML/JavaScript

```javascript
// Obtener lista de mapas
fetch('http://localhost:3000/api/maps')
  .then(response => response.json())
  .then(data => {
    console.log(`Mapas disponibles: ${data.total}`);
    data.maps.forEach(map => {
      console.log(`${map.parametros.num_circulos} × ${map.parametros.divisiones_por_circulo}`);
    });
  });

// Obtener mapa específico
fetch('http://localhost:3000/api/get-map', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    num_circulos: 10000,
    divisiones_por_circulo: 1300,
    tipo_mapeo: 'lineal',
    filtros: { primos: true, compuestos: true }
  })
})
  .then(response => response.json())
  .then(mapData => {
    // Renderizar mapa con mapData.elementos
    renderMap(mapData.elementos);
  });
```

## 🚦 Gestión del Proceso

### Iniciar generación automática al arrancar el servidor

```bash
# Guardar configuración de PM2
pm2 save

# Habilitar inicio automático
pm2 startup

# Ejecutar el comando que PM2 sugiere (varía según el sistema)
```

### Detener temporalmente sin eliminar

```bash
./pm2_manager.sh stop
# Para reanudar:
./pm2_manager.sh start
```

### Reiniciar si hay cambios en el código

```bash
./pm2_manager.sh restart
```

## 📊 Estimaciones de Tiempo y Espacio

### Tiempo de generación aproximado

| Configuración | Tiempo Estimado |
|---------------|-----------------|
| 5 × 12 (60 elementos) | < 1 segundo |
| 100 × 60 (6,000 elementos) | ~2 segundos |
| 1,000 × 360 (360,000 elementos) | ~30 segundos |
| 5,000 × 800 (4M elementos) | ~5 minutos |
| 10,000 × 1,300 (13M elementos) | ~15 minutos |

### Espacio en disco

- Mapa pequeño (< 1k elementos): ~5-50 KB
- Mapa medio (1k-10k elementos): ~50-500 KB
- Mapa grande (10k-100k elementos): ~500 KB - 2 MB
- Mapa muy grande (100k-1M elementos): ~2-10 MB
- Mapa extremo (> 1M elementos): ~10-50 MB

**Estimación total para toda la generación**: ~50-100 GB

## ⚠️ Consideraciones de Rendimiento

1. **Memoria**: Mapas extremos (13M elementos) pueden requerir 4-8 GB de RAM durante la generación
2. **CPU**: El proceso es CPU-intensivo, especialmente la criba de Eratóstenes
3. **Disco**: Asegurar suficiente espacio (100+ GB recomendado)
4. **Red**: Si se sirven mapas muy grandes, considerar CDN o compresión

## 🐛 Solución de Problemas

### El generador no inicia

```bash
# Verificar PM2
pm2 list

# Ver logs de error
./pm2_manager.sh logs

# Reintentar inicio
./pm2_manager.sh delete
./pm2_manager.sh start
```

### Proceso se detiene por falta de memoria

```bash
# Aumentar límite en ecosystem.config.js
max_memory_restart: '8G'

# Reiniciar
./pm2_manager.sh restart
```

### Archivos JSON no se generan

```bash
# Verificar permisos
chmod -R 755 static_maps/

# Verificar espacio en disco
df -h

# Ver errores específicos
tail -f logs/map-generator-error.log
```

## 📞 Soporte

Para más información o problemas, revisar:
- Logs en `logs/`
- Estadísticas en `background_generator_stats.json`
- Estado del proceso: `./pm2_manager.sh status`

---

**Desarrollado para soportar mapas de hasta 10,000 círculos × 1,300 segmentos** 🚀
