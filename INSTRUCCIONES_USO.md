# 📖 Instrucciones de Uso - Sistema PM2 de Mapas de Números Primos

## 🎯 Resumen

Sistema completo para generar y visualizar mapas de números primos con soporte para hasta **10,000 círculos × 1,300 segmentos = 13,000,000 números**.

---

## 🚀 Inicio Rápido (3 Pasos)

### Paso 1: Iniciar Generador PM2
```bash
./scripts/pm2_start_generator.sh
```
Esto iniciará el proceso de generación en segundo plano. El generador procesará 13,000,000 números y guardará los datos localmente.

### Paso 2: Iniciar Servidor Web
```bash
cd src && python3 unified_server_updated.py &
```
Esto iniciará el servidor en el puerto 3000.

### Paso 3: Abrir Aplicación
```
Navegador: http://localhost:3000/interactive
```

---

## 📊 Monitoreo del Generador

### Ver Estado Actual
```bash
./scripts/pm2_status_generator.sh
```

**Muestra**:
- Estado del proceso PM2
- Estadísticas de generación
- Progreso actual
- Almacenamiento usado

### Monitor en Tiempo Real
```bash
./scripts/pm2_monitor_progress.sh
```

**Actualiza cada 5 segundos**:
- Progreso porcentual
- Mapas generados
- Memoria usada
- Última actividad

### Ver Logs
```bash
./scripts/pm2_logs_generator.sh
# o directamente:
pm2 logs prime-map-generator
```

---

## 🎨 Usar el Mapa Interactivo

### 1. Abrir la Aplicación
```
http://localhost:3000/interactive
```

### 2. Configurar Parámetros

#### Círculos Concéntricos
- **Rango**: 5 - 10,000
- **Recomendado**: 
  - Pequeño: 10-50 (rápido)
  - Mediano: 100-500 (equilibrado)
  - Grande: 1,000-5,000 (detallado)
  - Máximo: 10,000 (requiere datos pre-generados)

#### Segmentos por Círculo
- **Rango**: 12 - 1,300
- **Recomendado**:
  - Pequeño: 24-60 (rápido)
  - Mediano: 100-300 (equilibrado)
  - Grande: 500-1,000 (detallado)
  - Máximo: 1,300 (requiere datos pre-generados)

#### Tipo de Mapeo
- **Lineal**: Secuencial, fácil de interpretar
- **Logarítmico**: Comprime números grandes
- **Arquímedes**: Espiral uniforme
- **Fibonacci**: Basado en razón áurea

### 3. Seleccionar Tipos de Primos
- ✅ Primos Regulares (azul)
- ✅ Primos Gemelos (rojo)
- ✅ Primos Primos (naranja)
- ✅ Primos Sexy (rosa)
- ✅ Sophie Germain (púrpura)
- ✅ Palindrómicos (dorado)
- ✅ Mersenne (cian)
- ✅ Fermat (verde lima)
- ✅ Compuestos (gris)

### 4. Generar Mapa
Click en "Generar Mapa Interactivo"

**El sistema automáticamente**:
1. Busca datos pre-generados
2. Si existen: Carga en <2 segundos
3. Si no existen: Genera dinámicamente
4. Muestra el origen en la consola del navegador

---

## 🔧 Gestión del Sistema

### Comandos PM2

#### Ver Procesos
```bash
pm2 list
```

#### Ver Detalles
```bash
pm2 show prime-map-generator
```

#### Monitor Interactivo
```bash
pm2 monit
```

#### Reiniciar Proceso
```bash
pm2 restart prime-map-generator
```

#### Detener Proceso
```bash
pm2 stop prime-map-generator
# o usar el script:
./scripts/pm2_stop_generator.sh
```

### Gestión del Servidor

#### Verificar si está corriendo
```bash
pgrep -f unified_server_updated.py
```

#### Detener servidor
```bash
pkill -f unified_server_updated.py
```

#### Reiniciar servidor
```bash
pkill -f unified_server_updated.py
cd src && python3 unified_server_updated.py &
```

---

## 📈 Entender el Progreso

### Tiempo de Generación Estimado

Para la configuración de **10,000 × 1,300 = 13,000,000 números**:

- **Generación de primos**: 5-10 minutos
- **Clasificación de números**: 15-25 minutos
- **Guardado de datos**: 2-5 minutos
- **Total estimado**: 20-40 minutos

### Reinicios del Proceso

**Es normal** que el proceso PM2 se reinicie varias veces:
- Generación de 13M números es muy intensiva en memoria
- PM2 reinicia automáticamente si se excede el límite (6GB)
- El proceso continúa desde donde quedó
- No se pierde progreso

### Verificar Progreso
```bash
# Ver progreso actual
cat src/data/generation_progress.json | python3 -m json.tool

# Ver estadísticas
cat src/data/generator_stats.json | python3 -m json.tool

# Ver logs recientes
pm2 logs prime-map-generator --lines 20 --nostream
```

---

## 💾 Datos Generados

### Ubicación
```
src/data/pregenerated_maps/data_{hash}.json.gz
```

### Formato
- **Compresión**: gzip
- **Tamaño**: ~200-300 MB por mapa de 13M números
- **Contenido**: Números, clasificación, posiciones

### Índice
```bash
# Ver mapas disponibles
cat src/data/index.json | python3 -m json.tool
```

---

## 🧪 Pruebas del Sistema

### Test 1: API Info
```bash
curl http://localhost:3000/api/info
```
**Esperado**: JSON con versión 3.5.0-pm2

### Test 2: Mapa Pequeño
```bash
curl -X POST http://localhost:3000/api/pregenerated-map \
  -H "Content-Type: application/json" \
  -d '{"num_circulos": 10, "divisiones_por_circulo": 24}'
```
**Esperado**: JSON con 240 elementos, source: "generated-dynamic"

### Test 3: Mapa Grande (Después de Generación)
```bash
curl -X POST http://localhost:3000/api/pregenerated-map \
  -H "Content-Type: application/json" \
  -d '{"num_circulos": 10000, "divisiones_por_circulo": 1300}'
```
**Esperado**: JSON con 13M elementos, source: "pregenerated" (cuando esté listo)

### Test 4: Frontend
1. Abrir: http://localhost:3000/interactive
2. Configurar: 100 círculos × 100 segmentos
3. Generar mapa
4. Verificar en consola del navegador el origen de datos

---

## ⚠️ Consideraciones Importantes

### Memoria
- El generador puede usar hasta **7GB de RAM** durante el procesamiento
- PM2 reiniciará el proceso si excede el límite configurado (6GB)
- Esto es **normal** y el proceso continuará automáticamente

### Tiempo
- La generación de 13M números tarda **20-40 minutos**
- El progreso se guarda continuamente
- Puedes detener y reiniciar sin perder progreso

### Espacio en Disco
- Cada mapa de 13M números ocupa ~**200-300 MB** comprimido
- Asegúrate de tener suficiente espacio disponible
- Verifica con: `du -sh src/data/`

### Reinicios Automáticos
- PM2 reinicia el proceso si:
  - Excede el límite de memoria (6GB)
  - Hay un error no manejado
  - El proceso se detiene inesperadamente
- **Máximo 10 reinicios** configurados
- Después de 10 reinicios, PM2 detiene el proceso

---

## 🔍 Troubleshooting

### Problema: Generador no inicia
```bash
# Verificar PM2
pm2 list

# Ver errores
pm2 logs prime-map-generator --err

# Reiniciar
pm2 restart prime-map-generator
```

### Problema: Servidor no responde
```bash
# Verificar proceso
pgrep -f unified_server_updated.py

# Ver logs
tail -f logs/pm2-generator-out.log

# Reiniciar
pkill -f unified_server_updated.py
cd src && python3 unified_server_updated.py &
```

### Problema: Generación muy lenta
- **Normal**: 13M números tarda 20-40 minutos
- **Verificar memoria**: `pm2 monit`
- **Ver progreso**: `./scripts/pm2_status_generator.sh`

### Problema: Muchos reinicios
- **Causa**: Memoria insuficiente
- **Solución**: Aumentar límite en `ecosystem.config.js`
- **Alternativa**: Esperar a que complete (reinicia automáticamente)

---

## 📚 Documentación Adicional

- **README_PM2.md**: Guía de inicio rápido
- **docs/PM2_GENERATOR_GUIDE.md**: Guía completa del generador
- **docs/ACTUALIZACION_PM2_13M.md**: Detalles de la actualización
- **RESUMEN_IMPLEMENTACION.md**: Resumen de implementación

---

## 🎉 Características del Sistema

### ✅ Implementado
- [x] Soporte para 13,000,000 números
- [x] Generación en segundo plano con PM2
- [x] Almacenamiento local optimizado
- [x] Compresión gzip de datos
- [x] API con fallback inteligente
- [x] Frontend actualizado
- [x] Scripts de gestión completos
- [x] Monitoreo en tiempo real
- [x] Auto-restart automático
- [x] Documentación completa

### 🌟 Beneficios
1. **Rendimiento**: Mapas pre-generados cargan en <2s
2. **Escalabilidad**: Hasta 13M números soportados
3. **Confiabilidad**: PM2 gestiona todo automáticamente
4. **Optimización**: Compresión reduce tamaño en ~70%
5. **Flexibilidad**: Fallback a generación dinámica
6. **Monitoreo**: Progreso y estadísticas en tiempo real

---

## 📞 Comandos de Referencia Rápida

```bash
# GESTIÓN PM2
./scripts/pm2_start_generator.sh      # Iniciar
./scripts/pm2_status_generator.sh     # Estado
./scripts/pm2_monitor_progress.sh     # Monitor
./scripts/pm2_logs_generator.sh       # Logs
./scripts/pm2_stop_generator.sh       # Detener

# SERVIDOR
cd src && python3 unified_server_updated.py &  # Iniciar
curl http://localhost:3000/api/info            # Verificar
pkill -f unified_server_updated.py             # Detener

# VERIFICACIÓN
pm2 list                                       # Procesos PM2
ls -lh src/data/pregenerated_maps/             # Mapas generados
cat src/data/index.json | python3 -m json.tool # Índice

# PRUEBAS
curl http://localhost:3000/api/info            # Info del sistema
curl -X POST http://localhost:3000/api/pregenerated-map \
  -H "Content-Type: application/json" \
  -d '{"num_circulos": 100, "divisiones_por_circulo": 100}'
```

---

**✅ Sistema Listo para Usar**  
**🚀 Generador PM2 Activo**  
**📊 Soporta hasta 13,000,000 Números**  
**⚡ Rendimiento Optimizado**
