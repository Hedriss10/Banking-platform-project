import os
from decouple import config as decouple_config

class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Upload de 16 MB
    SECRET_KEY = os.urandom(24)

class TestingConfig(Config):
    TESTING = True
    DEVELOPMENT = True
    DEBUG = True
    DEBUG_TB_ENABLED = True
    PORT_HOST = 8000
    SQLALCHEMY_DATABASE_URI = decouple_config('TEST_DATABASE_URL', default='sqlite:///:memory:')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = decouple_config('DATABASE_URL', default='sqlite:///production.db')
    DEBUG = False
    DEBUG_TB_ENABLED = False
    PORT_HOST = 8000
    IP_HOST = "0.0.0.0"
    URL_MAIN = f'http://{IP_HOST}:{PORT_HOST}/'

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    DEBUG_TB_ENABLED = True
    PORT_HOST = 8000
    SQLALCHEMY_DATABASE_URI = decouple_config('DEV_DATABASE_URL', default='sqlite:///dev.db')
    IP_HOST = "localhost"
    PORT_HOST = 5500
    URL_MAIN = f'http://{IP_HOST}:{PORT_HOST}/'

config_by_name = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig
)

flask_env = os.getenv('FLASK_ENV', 'development')

if flask_env not in config_by_name:
    raise ValueError(f"Invalid value for FLASK_ENV: {flask_env}. Must be one of {list(config_by_name.keys())}")

config = config_by_name[flask_env]

