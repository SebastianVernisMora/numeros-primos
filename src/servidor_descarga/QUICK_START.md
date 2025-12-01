# 🚀 Inicio Rápido - Sistema de Mapas Primos

## En 5 Pasos

### 1️⃣ Instalación (Primera vez)

```bash
cd /vercel/sandbox/src/servidor_descarga
chmod +x setup_pm2_system.sh
./setup_pm2_system.sh
```

**Tiempo**: ~5 minutos

---

### 2️⃣ Iniciar Generador de Mapas

```bash
./pm2_manager.sh start
```

**Resultado esperado**:
```
✅ Generador iniciado exitosamente
🆔 PID: 12345
📊 Estado: CORRIENDO
```

---

### 3️⃣ Ver Progreso (Opcional)

```bash
# Ver logs en tiempo real
./pm2_manager.sh logs

# Ver estadísticas
./pm2_manager.sh stats
```

**Ejemplo de salida**:
```
🔨 [15/2340] Generando: 100×60 = 6,000 elementos
  ✅ Guardado: abc123def456 (145.3 KB) en 2.1s
📊 Progreso: 15 generados | 15 totales | 2.1 MB
```

---

### 4️⃣ Iniciar Servidor Web

```bash
python3 static_maps_server.py
```

**Resultado esperado**:
```
🚀 Iniciando Servidor de Mapas Pregenerados
📁 Directorio de mapas: /vercel/sandbox/src/servidor_descarga/static_maps
🗺️ Capacidad: 10,000 círculos × 1,300 segmentos
✅ Servidor listo - 15 mapas cargados
🌐 Escuchando en http://0.0.0.0:3000
```

---

### 5️⃣ Acceder a la Interfaz

**Opción A**: Abrir en navegador
```
http://localhost:3000
```

**Opción B**: Usar la interfaz HTML directamente
```bash
# Abrir index_pregenerated.html en el navegador
```

---

## 🎯 Ejemplo de Uso

### Cargar un mapa de 100 círculos × 60 segmentos

1. En la interfaz web:
   - Círculos: `100`
   - Segmentos: `60`
   - Tipo de Mapeo: `Lineal`
   - Click en **"Cargar Mapa"**

2. Resultado:
   - Mapa renderizado con 6,000 elementos
   - Estadísticas actualizadas
   - Interacción con tooltips al pasar el mouse

---

## 📊 Probar con API

### Listar mapas disponibles

```bash
curl http://localhost:3000/api/maps | jq
```

### Obtener mapa específico

```bash
curl -X POST http://localhost:3000/api/get-map \
  -H "Content-Type: application/json" \
  -d '{
    "num_circulos": 100,
    "divisiones_por_circulo": 60,
    "tipo_mapeo": "lineal",
    "filtros": {
      "primos": true,
      "compuestos": true
    }
  }' | jq
```

### Ver estadísticas del servidor

```bash
curl http://localhost:3000/api/stats | jq
```

---

## 🛠️ Comandos Útiles

```bash
# Ver estado del generador
./pm2_manager.sh status

# Ver logs en tiempo real
./pm2_manager.sh logs

# Ver estadísticas detalladas
./pm2_manager.sh stats

# Reiniciar generador
./pm2_manager.sh restart

# Detener generador
./pm2_manager.sh stop

# Limpiar logs antiguos
./pm2_manager.sh clean
```

---

## ⚡ Generar Mapa Extremo (10,000 × 1,300)

### Usando la Interfaz

1. Círculos: `10000`
2. Segmentos: `1300`
3. Tipo de Mapeo: `Lineal`
4. Click en **"Cargar Mapa"**

**Nota**: El mapa debe estar pregenerado (puede tardar ~15 minutos en generarse)

### Usando la API

```bash
curl -X POST http://localhost:3000/api/get-map \
  -H "Content-Type: application/json" \
  -d '{
    "num_circulos": 10000,
    "divisiones_por_circulo": 1300,
    "tipo_mapeo": "lineal",
    "filtros": {"primos": true, "compuestos": true}
  }' | jq '.metadata'
```

---

## 🔍 Verificar que Todo Funciona

### 1. Verificar generador

```bash
./pm2_manager.sh status
```

**Esperado**: Estado "online" o "running"

### 2. Verificar archivos generados

```bash
ls -lh static_maps/data_*.json | wc -l
```

**Esperado**: Número creciente de archivos

### 3. Verificar servidor web

```bash
curl http://localhost:3000/health
```

**Esperado**: `{"status": "healthy", ...}`

---

## 🐛 Problemas Comunes

### Generador no inicia

```bash
# Ver errores
./pm2_manager.sh logs

# Reintentar
./pm2_manager.sh delete
./pm2_manager.sh start
```

### Servidor web no responde

```bash
# Verificar si está corriendo
ps aux | grep static_maps_server

# Verificar puerto
netstat -tuln | grep 3000

# Reiniciar
pkill -f static_maps_server
python3 static_maps_server.py
```

### Mapa no encontrado

```bash
# Ver mapas disponibles
curl http://localhost:3000/api/maps | jq '.total'

# Esperar a que se genere o usar parámetros disponibles
```

---

## 📈 Monitorear Generación

### Ver progreso en tiempo real

```bash
watch -n 5 './pm2_manager.sh stats'
```

### Ver archivos generados

```bash
watch -n 10 'ls -1 static_maps/data_*.json | wc -l'
```

### Ver tamaño total

```bash
watch -n 30 'du -sh static_maps/'
```

---

## 🎉 ¡Listo!

Ya tienes el sistema funcionando. Ahora puedes:

✅ Generar mapas de hasta 10,000 × 1,300
✅ Acceder a ellos vía API REST
✅ Visualizarlos en la interfaz web
✅ Monitorear el progreso en tiempo real

Para más detalles, consulta: **README_PM2_MAPS.md**

---

**Happy mapping! 🗺️✨**
