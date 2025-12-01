# Sistema PM2 de Pre-generación de Mapas de Números Primos

## 🚀 Inicio Rápido

### Iniciar el Sistema Completo
```bash
# 1. Iniciar generador PM2 (en segundo plano)
./scripts/pm2_start_generator.sh

# 2. Iniciar servidor web (puerto 3000)
cd src && python3 unified_server_updated.py &

# 3. Verificar estado
./scripts/pm2_status_generator.sh
curl http://localhost:3000/api/info
```

### Acceder a la Aplicación
```
🌐 Página principal: http://localhost:3000/
🗺️ Mapa interactivo: http://localhost:3000/interactive
🎨 Generador imágenes: http://localhost:3000/images
```

## 📊 Capacidades del Sistema

### Configuración Máxima Soportada
- **Círculos**: 10,000
- **Segmentos por círculo**: 1,300
- **Total de números**: 13,000,000
- **Tipos de primos**: 8 categorías diferentes

### Modos de Operación

#### 1. Datos Pre-generados (Recomendado)
- ✅ Carga en <2 segundos
- ✅ Generados por PM2 en segundo plano
- ✅ Almacenados localmente comprimidos
- ✅ Disponibles inmediatamente

#### 2. Generación Dinámica (Fallback)
- ⚡ Se activa si no hay datos pre-generados
- ⚡ Configuraciones pequeñas: <5 segundos
- ⚡ Configuraciones grandes: 1-5 minutos

## 🔧 Gestión del Generador PM2

### Comandos Principales
```bash
# Iniciar generador
./scripts/pm2_start_generator.sh

# Ver estado y progreso
./scripts/pm2_status_generator.sh

# Monitor en tiempo real
./scripts/pm2_monitor_progress.sh

# Ver logs en vivo
./scripts/pm2_logs_generator.sh

# Detener generador
./scripts/pm2_stop_generator.sh
```

### Comandos PM2 Directos
```bash
pm2 list                          # Lista de procesos
pm2 show prime-map-generator      # Detalles del proceso
pm2 monit                         # Monitor interactivo
pm2 logs prime-map-generator      # Logs en tiempo real
pm2 restart prime-map-generator   # Reiniciar proceso
pm2 stop prime-map-generator      # Detener proceso
```

## 📡 API Endpoints

### 1. Mapas Pre-generados (Nuevo)
```bash
POST /api/pregenerated-map
```

**Parámetros**:
```json
{
  "num_circulos": 10000,
  "divisiones_por_circulo": 1300,
  "tipo_mapeo": "lineal"
}
```

**Respuesta**:
- `source`: "pregenerated" o "generated-dynamic"
- `cache_hit`: true o false
- `elementos`: Array de números con clasificación
- `estadisticas`: Contadores y densidad de primos

**Ejemplo**:
```bash
curl -X POST http://localhost:3000/api/pregenerated-map \
  -H "Content-Type: application/json" \
  -d '{"num_circulos": 10000, "divisiones_por_circulo": 1300}'
```

### 2. Mapa Interactivo (Existente)
```bash
POST /api/interactive-map
```

### 3. Generador de Imágenes (Existente)
```bash
POST /api/generate-image
```

### 4. Información del Sistema
```bash
GET /api/info
```

## 💾 Almacenamiento de Datos

### Estructura de Directorios
```
src/data/
├── pregenerated_maps/          # Mapas pre-generados
│   └── data_{hash}.json.gz     # Archivos comprimidos
├── index.json                  # Índice de mapas disponibles
├── generation_progress.json    # Progreso de generación
└── generator_stats.json        # Estadísticas del generador
```

### Formato de Datos
- **Compresión**: gzip (ahorro ~70%)
- **Tamaño por mapa**: ~200-300 MB (13M números)
- **Hash**: MD5 de configuración (identificador único)

## 📈 Monitoreo y Estadísticas

### Ver Progreso de Generación
```bash
# Opción 1: Script de estado
./scripts/pm2_status_generator.sh

# Opción 2: Archivo de progreso
cat src/data/generation_progress.json | python3 -m json.tool

# Opción 3: Estadísticas completas
cat src/data/generator_stats.json | python3 -m json.tool
```

### Ver Mapas Generados
```bash
# Listar archivos
ls -lh src/data/pregenerated_maps/

# Ver índice
cat src/data/index.json | python3 -m json.tool

# Espacio usado
du -sh src/data/
```

## 🎨 Uso del Frontend

### Configuración del Mapa
1. Abrir: http://localhost:3000/interactive
2. Configurar parámetros:
   - **Círculos**: 5 - 10,000
   - **Segmentos**: 12 - 1,300
   - **Tipo de mapeo**: Lineal, Logarítmico, Arquímedes, Fibonacci
3. Seleccionar tipos de primos a mostrar
4. Generar mapa

### Indicadores
- **Datos pre-generados**: Carga rápida (<2s)
- **Generación dinámica**: Mensaje "generando..." con tiempo estimado
- **Consola del navegador**: Muestra origen de datos

## ⚡ Optimizaciones Implementadas

### Memoria
- ✅ Procesamiento por chunks de 100,000 números
- ✅ Liberación de memoria con gc.collect()
- ✅ Límite PM2: 6GB máximo
- ✅ Compresión gzip de archivos

### Rendimiento
- ✅ Criba de Eratóstenes optimizada
- ✅ Procesamiento por lotes
- ✅ Cache en disco (no RAM)
- ✅ Índice para búsqueda rápida

### Confiabilidad
- ✅ Auto-restart de PM2
- ✅ Manejo de señales de terminación
- ✅ Guardado de progreso continuo
- ✅ Logs detallados y rotativos

## 🔍 Troubleshooting

### El generador no inicia
```bash
pm2 list
pm2 logs prime-map-generator --err
pm2 restart prime-map-generator
```

### El servidor no responde
```bash
# Verificar si está corriendo
pgrep -f unified_server_updated.py

# Reiniciar servidor
pkill -f unified_server_updated.py
cd src && python3 unified_server_updated.py &

# Verificar puerto
curl http://localhost:3000/api/info
```

### Generación muy lenta
- **Normal**: 13M números tarda 20-40 minutos
- **Verificar**: `pm2 monit` para ver uso de recursos
- **Logs**: `pm2 logs prime-map-generator`

### Mapas no se cargan
```bash
# Verificar archivos
ls -lh src/data/pregenerated_maps/

# Verificar índice
cat src/data/index.json

# Ver logs del servidor
tail -f logs/pm2-generator-out.log
```

## 📚 Documentación Adicional

- **Guía Completa PM2**: `docs/PM2_GENERATOR_GUIDE.md`
- **Actualización 13M**: `docs/ACTUALIZACION_PM2_13M.md`
- **Servidor Unificado**: `docs/SERVIDOR_UNIFICADO_ACTUALIZADO.md`
- **Guía de Desarrollo**: `src/servidor_descarga/CRUSH.md`

## 🎯 Características Principales

### Sistema de Pre-generación
- ✅ Generación en segundo plano con PM2
- ✅ Almacenamiento local optimizado
- ✅ Compresión gzip automática
- ✅ Índice de búsqueda rápida
- ✅ Progreso y estadísticas en tiempo real

### API Inteligente
- ✅ Prioriza datos pre-generados
- ✅ Fallback a generación dinámica
- ✅ Respuestas optimizadas
- ✅ Compresión de transferencia

### Frontend Mejorado
- ✅ Soporte para 13M números
- ✅ Carga automática desde pre-generados
- ✅ Indicadores de origen de datos
- ✅ Mensajes de ayuda contextuales

## 🌟 Beneficios

1. **⚡ Rendimiento**: Mapas pre-generados cargan en <2 segundos
2. **📈 Escalabilidad**: Soporta hasta 13M números
3. **🔄 Confiabilidad**: PM2 gestiona el proceso automáticamente
4. **💾 Optimización**: Compresión reduce tamaño en ~70%
5. **🛡️ Fallback**: Generación dinámica siempre disponible
6. **📊 Monitoreo**: Estadísticas y progreso en tiempo real
7. **🎯 Flexibilidad**: Múltiples configuraciones soportadas

---

**✅ Sistema Completamente Implementado y Funcionando**  
**🚀 Generador PM2 Activo en Segundo Plano**  
**📊 Soporta hasta 13,000,000 Números**  
**💾 Almacenamiento Local Optimizado con Compresión**  
**🎨 Frontend Actualizado con Carga Inteligente**
