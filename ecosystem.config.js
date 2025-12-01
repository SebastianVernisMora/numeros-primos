module.exports = {
  apps: [
    {
      name: 'prime-map-generator',
      script: './src/pm2_data_generator.py',
      interpreter: 'python3',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '8G',
      error_file: './logs/pm2-generator-error.log',
      out_file: './logs/pm2-generator-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      env: {
        NODE_ENV: 'production',
        PYTHONUNBUFFERED: '1'
      },
      restart_delay: 5000,
      max_restarts: 50,
      min_uptime: '10s',
      listen_timeout: 10000,
      kill_timeout: 5000,
      wait_ready: false
    }
  ]
};
