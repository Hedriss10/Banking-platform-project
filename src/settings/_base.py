import os
from decouple import config as decouple_config
from dotenv import load_dotenv

load_dotenv()

class Config(object):
    ENV = os.getenv("FLASK_ENV", "development")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    SECRET_KEY = os.urandom(24)

class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = os.getenv("DEV_DEBUG")
    PORT = os.getenv("PORT", "5001")
    DATABASE = os.getenv("DB_DEV_DATABASE")
    USERNAME = os.getenv("DB_DEV_USERNAME")
    PASSWORD =  os.getenv("DB_DEV_PASSWORD")
    DB_HOST = os.getenv("DB_DEV_HOST")
    DB_PORT = os.getenv("DB_DEV_PORT")
    

class ProductionConfig(Config):    
    ENV = "production"
    DEBUG = os.getenv("PRD_DEBUG")
    PORT = os.getenv("PORT", "5002")
    DATABASE = os.getenv("DB_PRD_DATABASE")
    USERNAME = os.getenv("DB_PRD_USERNAME")
    PASSWORD =  os.getenv("DB_PRD_PASSWORD")
    DB_HOST = os.getenv("DB_PRD_HOST")
    DB_PORT = os.getenv("DB_PRD_PORT")

config_by_name = {'development': DevelopmentConfig, 'production': ProductionConfig}

flask_env = os.getenv('FLASK_ENV', 'development')
if flask_env not in config_by_name:
    raise ValueError(f"Invalid value for FLASK_ENV: {flask_env}. Must be one of {list(config_by_name.keys())}")

config = config_by_name[flask_env]