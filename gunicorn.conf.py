import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

bind = "0.0.0.0:8001"
workers = 4
threads = 2
timeout = 60
preload_app = True
accesslog = "-"
errorlog = "-"
loglevel = "info"