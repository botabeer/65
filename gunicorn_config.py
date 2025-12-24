import os
import multiprocessing

bind = f"0.0.0.0:{os.getenv('PORT', '10000')}"
backlog = 2048

workers = int(os.getenv('WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

proc_name = 'bot65'

daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

keyfile = None
certfile = None
