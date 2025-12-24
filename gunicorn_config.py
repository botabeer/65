import os
import multiprocessing

bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
workers = int(os.getenv('WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

accesslog = '-'
errorlog = '-'
loglevel = 'info'

preload_app = True
daemon = False
