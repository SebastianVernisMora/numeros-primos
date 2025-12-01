module.exports = {
  apps: [{
    name: 'map-generator',
    script: 'background_map_generator.py',
    interpreter: 'python3',
    cwd: '/vercel/sandbox/src/servidor_descarga',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '4G',
    error_file: 'logs/map-generator-error.log',
    out_file: 'logs/map-generator-out.log',
    log_file: 'logs/map-generator-combined.log',
    time: true,
    env: {
      NODE_ENV: 'production',
      PYTHONUNBUFFERED: '1'
    },
    // Configuración de reinicio
    restart_delay: 4000,
    max_restarts: 10,
    min_uptime: '10s',
    // Configuración de logs
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    // Configuración de monitoreo
    pmx: true,
    vizion: false,
    // Configuración de cron para reiniciar si se completa
    cron_restart: '0 0 * * *', // Reiniciar a medianoche si es necesario
    // Configuración de señales
    kill_timeout: 5000,
    listen_timeout: 3000,
    shutdown_with_message: true
  }]
};
