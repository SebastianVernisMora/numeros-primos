# Project Repository - Mapas de Números Primos

This repository contains a complete system for generating and visualizing prime number maps with support for up to **13,000,000 numbers** (10,000 circles × 1,300 segments).

## 🚀 Quick Start

### Start the Complete System
```bash
# 1. Start PM2 background generator
./scripts/pm2_start_generator.sh

# 2. Start web server (port 3000)
cd src && python3 unified_server_updated.py &

# 3. Access application
# Open: http://localhost:3000/interactive
```

### Monitor Progress
```bash
./scripts/pm2_status_generator.sh     # Status
./scripts/pm2_monitor_progress.sh     # Real-time monitor
pm2 logs prime-map-generator          # Live logs
```

## Directory Structure

```
├── src/                    # Source code files
│   ├── pm2_data_generator.py      # PM2 background data generator
│   ├── unified_server_updated.py  # Main server (port 3000)
│   ├── interactive_updated.html   # Interactive map frontend
│   ├── image_creator.py           # Image generator
│   ├── data/                      # Pre-generated data storage
│   │   ├── pregenerated_maps/     # Compressed map data
│   │   ├── index.json             # Map index
│   │   └── generator_stats.json   # Generator statistics
│   └── servidor_descarga/         # Download server module
├── scripts/               # Shell scripts for deployment and management
│   ├── pm2_start_generator.sh     # Start PM2 generator
│   ├── pm2_stop_generator.sh      # Stop PM2 generator
│   ├── pm2_status_generator.sh    # View status
│   ├── pm2_logs_generator.sh      # View logs
│   └── pm2_monitor_progress.sh    # Real-time monitor
├── docs/                  # Documentation and updates
│   ├── PM2_GENERATOR_GUIDE.md     # Complete PM2 guide
│   └── ACTUALIZACION_PM2_13M.md   # Update details
├── config/                # Configuration files and services
├── ecosystem.config.js    # PM2 configuration
├── README_PM2.md          # PM2 quick start guide
├── INSTRUCCIONES_USO.md   # Usage instructions
└── README.md              # This file
```

## 🌟 Features

### PM2 Background Generation System
- ✅ Generates data for up to 13,000,000 numbers
- ✅ Runs in background with PM2 process manager
- ✅ Auto-restart on errors
- ✅ Real-time progress monitoring
- ✅ Gzip compression (~70% space saving)

### Intelligent API
- ✅ Prioritizes pre-generated data (loads in <2s)
- ✅ Automatic fallback to dynamic generation
- ✅ 4 active endpoints
- ✅ CORS enabled

### Updated Frontend
- ✅ Supports up to 10,000 circles × 1,300 segments
- ✅ Automatic loading from pre-generated data
- ✅ Data source indicators
- ✅ Help messages for large configurations

## Components

### Source Code (`src/`)
- **pm2_data_generator.py**: PM2 background data generator (NEW)
- **unified_server_updated.py**: Main server with pre-generation support (UPDATED)
- **interactive_updated.html**: Interactive map frontend (UPDATED)
- **image_creator.py**: PNG image generator
- **data/**: Pre-generated data storage (NEW)

### Scripts (`scripts/`)
- **PM2 Management**: 5 scripts for PM2 control (NEW)
- **Deployment**: Deployment scripts
- **Management**: Application management scripts

### Documentation (`docs/`)
- **PM2_GENERATOR_GUIDE.md**: Complete PM2 guide (NEW)
- **ACTUALIZACION_PM2_13M.md**: Update details (NEW)
- Project updates and changelogs
- Deployment guides

### Configuration (`config/`)
- **ecosystem.config.js**: PM2 configuration (NEW)
- Service configuration files

## Getting Started

### Quick Start (3 Steps)
```bash
# 1. Start PM2 generator
./scripts/pm2_start_generator.sh

# 2. Start web server
cd src && python3 unified_server_updated.py &

# 3. Open browser
# http://localhost:3000/interactive
```

### Monitor Progress
```bash
./scripts/pm2_status_generator.sh     # View status
./scripts/pm2_monitor_progress.sh     # Real-time monitor
pm2 logs prime-map-generator          # Live logs
```

## 📚 Documentation

- **README_PM2.md** - PM2 quick start guide
- **INSTRUCCIONES_USO.md** - Detailed usage instructions
- **IMPLEMENTACION_COMPLETA.md** - Complete implementation summary
- **docs/PM2_GENERATOR_GUIDE.md** - Complete PM2 guide

## Notes

- Pre-generated data is stored in `src/data/pregenerated_maps/`
- Each map of 13M numbers takes ~20-40 minutes to generate
- Pre-generated maps load in <2 seconds
- System automatically falls back to dynamic generation if needed
- All image files are ignored by git (see `.gitignore`)