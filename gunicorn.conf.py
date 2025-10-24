"""
Gunicorn configuration tailored for Railway deployment.

Key behaviors:
- Bind to the port provided by the environment (PORT)
- Log to stdout/stderr for platform log collection
- Sensible worker defaults with WEB_CONCURRENCY override
"""

import os

# Bind to the port Railway provides
PORT = os.getenv("PORT", "5000")
bind = f"0.0.0.0:{PORT}"

# Workers: allow override via WEB_CONCURRENCY, default to 2
workers = int(os.getenv("WEB_CONCURRENCY", "2"))
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Logging to stdout/stderr (Railway ingests these)
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = (
    '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
)

# Process naming
proc_name = os.getenv("PROC_NAME", "melodyai")

# Security / proxy headers
forwarded_allow_ips = "*"
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on',
}
