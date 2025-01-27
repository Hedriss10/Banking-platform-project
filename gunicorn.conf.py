import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

bind = f"0.0.0.0:{os.getenv('DEV_PORT', '8001')}"
workers = 4
threads = 2
timeout = 60
preload_app = True
accesslog = "-"
errorlog = "-"
loglevel = "info"
wsgi_app = "src.app:create_app()"