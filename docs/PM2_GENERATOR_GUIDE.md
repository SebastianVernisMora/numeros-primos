# Guía del Generador PM2 de Mapas de Números Primos

## 📋 Descripción

Sistema de pre-generación de datos para mapas de números primos usando PM2 como gestor de procesos en segundo plano. Soporta configuraciones de hasta **10,000 círculos × 1,300 segmentos = 13,000,000 números**.

## 🚀 Inicio Rápido

### 1. Iniciar el Generador
```bash
./scripts/pm2_start_generator.sh
```

### 2. Ver Estado y Progreso
```bash
./scripts/pm2_status_generator.sh
```

### 3. Ver Logs en Tiempo Real
```bash
./scripts/pm2_logs_generator.sh
# o directamente:
pm2 logs prime-map-generator
```

### 4. Detener el Generador
```bash
./scripts/pm2_stop_generator.sh
```

## 📊 Configuración

### Objetivo de Generación
El generador está configurado para crear datos para:
- **Círculos**: 10,000
- **Segmentos por círculo**: 1,300
- **Total de números**: 13,000,000
- **Tipo de mapeo**: Lineal

### Archivos de Configuración

#### `ecosystem.config.js`
Configuración de PM2:
- **Nombre del proceso**: `prime-map-generator`
- **Script**: `./src/pm2_data_generator.py`
- **Intérprete**: Python 3
- **Auto-restart**: Sí
- **Límite de memoria**: 6GB
- **Logs**: `./logs/pm2-generator-*.log`

#### `pm2_data_generator.py`
Generador principal:
- Calcula números primos usando Criba de Eratóstenes optimizada
- Clasifica primos por tipo (gemelos, Mersenne, Fermat, etc.)
- Guarda datos en formato JSON comprimido (gzip)
- Actualiza índice de mapas generados
- Reporta progreso y estadísticas

## 💾 Almacenamiento

### Estructura de Directorios
```
src/
├── data/
│   ├── pregenerated_maps/          # Mapas pre-generados
│   │   ├── data_abc123.json.gz     # Datos comprimidos
│   │   └── ...
│   ├── index.json                  # Índice de mapas
│   ├── generation_progress.json    # Progreso actual
│   └── generator_stats.json        # Estadísticas del generador
└── pm2_data_generator.py           # Script generador
```

### Formato de Datos

#### Archivo de Mapa (`data_{hash}.json.gz`)
```json
{
  "metadata": {
    "num_circulos": 10000,
    "divisiones_por_circulo": 1300,
    "tipo_mapeo": "lineal",
    "total_numeros": 13000000,
    "generated_at": "2025-12-01T...",
    "generation_time_seconds": 1234.56,
    "version": "2.0-pm2"
  },
  "elementos": [
    {
      "numero": 1,
      "circulo": 0,
      "segmento": 0,
      "es_primo": false,
      "tipos": ["compuesto"],
      "posicion": {
        "radio": 1,
        "angulo": 0,
        "x": 1.0,
        "y": 0.0
      }
    }
  ],
  "estadisticas": {
    "total_elementos": 13000000,
    "total_primos": 850000,
    "total_compuestos": 12150000,
    "densidad_primos": 6.54
  }
}
```

#### Índice (`index.json`)
```json
{
  "maps": {
    "abc123def456": {
      "num_circulos": 10000,
      "divisiones_por_circulo": 1300,
      "tipo_mapeo": "lineal",
      "total_elementos": 13000000,
      "file_size_mb": 245.67,
      "generated_at": "2025-12-01T..."
    }
  },
  "total_count": 1,
  "total_size_mb": 245.67,
  "generated_at": "2025-12-01T...",
  "last_updated": "2025-12-01T..."
}
```

## 🔧 API del Servidor

### Endpoint de Mapas Pre-generados
```bash
# Obtener mapa pre-generado (o generar dinámicamente si no existe)
curl -X POST http://localhost:3000/api/pregenerated-map \
  -H "Content-Type: application/json" \
  -d '{
    "num_circulos": 10000,
    "divisiones_por_circulo": 1300,
    "tipo_mapeo": "lineal"
  }'
```

**Respuesta**:
- Si existe pre-generado: `"source": "pregenerated"`, `"cache_hit": true`
- Si se genera dinámicamente: `"source": "generated-dynamic"`, `"cache_hit": false`

### Información del Sistema
```bash
curl http://localhost:3000/api/info
```

Incluye información sobre mapas pre-generados disponibles.

## 📈 Monitoreo

### Comandos PM2
```bash
# Lista de procesos
pm2 list

# Estado detallado
pm2 show prime-map-generator

# Monitoreo en tiempo real
pm2 monit

# Reiniciar proceso
pm2 restart prime-map-generator

# Detener proceso
pm2 stop prime-map-generator

# Eliminar proceso
pm2 delete prime-map-generator
```

### Archivos de Estado

#### `generator_stats.json`
```json
{
  "started_at": "2025-12-01T14:29:21",
  "maps_generated": 1,
  "maps_skipped": 0,
  "errors": 0,
  "current_config": null,
  "last_activity": "2025-12-01T14:35:42",
  "total_size_mb": 245.67,
  "finished_at": "2025-12-01T14:35:42"
}
```

#### `generation_progress.json`
```json
{
  "current_index": 1,
  "total_configs": 1,
  "progress_percent": 100.0,
  "maps_generated": 1,
  "maps_skipped": 0,
  "last_updated": "2025-12-01T14:35:42"
}
```

## 🎯 Uso en el Frontend

El frontend (`interactive_updated.html`) automáticamente:
1. Intenta cargar desde `/api/pregenerated-map` primero
2. Si no existe, usa `/api/interactive-map` (generación dinámica)
3. Muestra indicador de origen de datos en consola

### Configuración Máxima Soportada
- **Círculos**: 5 - 10,000
- **Segmentos**: 12 - 1,300
- **Total máximo**: 13,000,000 números

## ⚡ Optimizaciones

### Memoria
- Procesamiento por chunks de 100,000 números
- Liberación de memoria con `gc.collect()` periódica
- Compresión gzip de archivos JSON (ahorro ~70%)

### Rendimiento
- Criba de Eratóstenes optimizada
- Procesamiento por lotes para números grandes
- Índice en memoria para búsqueda rápida

### Almacenamiento
- Archivos comprimidos con gzip
- Hash MD5 para identificación única
- Índice centralizado para búsqueda rápida

## 🔍 Troubleshooting

### El generador no inicia
```bash
# Verificar PM2
pm2 list

# Ver logs de error
pm2 logs prime-map-generator --err

# Reiniciar
pm2 restart prime-map-generator
```

### Generación muy lenta
- Normal para 13M números (puede tardar 20-30 minutos)
- Verificar uso de memoria: `pm2 monit`
- Revisar logs: `pm2 logs prime-map-generator`

### Archivos no se generan
```bash
# Verificar permisos
ls -la src/data/

# Crear directorios manualmente
mkdir -p src/data/pregenerated_maps

# Ver logs detallados
tail -f logs/pm2-generator-out.log
```

### Servidor no encuentra mapas pre-generados
```bash
# Verificar que existen
ls -lh src/data/pregenerated_maps/

# Verificar índice
cat src/data/index.json | python3 -m json.tool

# Reiniciar servidor
pkill -f unified_server_updated.py
python3 src/unified_server_updated.py
```

## 📝 Notas Importantes

1. **Tiempo de Generación**: Para 13M números, espera 20-40 minutos dependiendo del hardware
2. **Espacio en Disco**: Cada mapa comprimido ocupa ~200-300 MB
3. **Memoria RAM**: El generador puede usar hasta 6GB durante el procesamiento
4. **Auto-restart**: PM2 reiniciará automáticamente si hay errores
5. **Persistencia**: Los datos se guardan localmente y persisten entre reinicios

## 🎉 Beneficios

- ✅ **Rendimiento**: Mapas pre-generados se cargan en <1 segundo
- ✅ **Escalabilidad**: Soporta hasta 13M números sin problemas
- ✅ **Confiabilidad**: PM2 gestiona el proceso automáticamente
- ✅ **Optimización**: Compresión gzip reduce tamaño en ~70%
- ✅ **Fallback**: Generación dinámica si no existe pre-generado
- ✅ **Monitoreo**: Estadísticas y progreso en tiempo real
