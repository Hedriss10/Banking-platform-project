import os
from decouple import config as decouple_config
from dotenv import load_dotenv

load_dotenv()

class Config(object):
    ENV = os.getenv("FLASK_ENV", "development")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URL")
    SQLALCHEMY_POOL_RECYCLE = 3600 

class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = os.getenv("DEV_DEBUG")
    PORT = os.getenv("PORT", "5001")
    DEV_DATABASE_URL = os.getenv("DEV_DATABASE_URL")

class ProductionConfig(Config):    
    ENV = "production"
    DEBUG = os.getenv("PRD_DEBUG")
    PORT = os.getenv("PORT", "5002")
    PRD_DATABASE_URL = os.getenv("PRD_DATABASE_URL")
    
    

config_by_name = {'development': DevelopmentConfig, 'production': ProductionConfig}

flask_env = os.getenv('FLASK_ENV', 'development')
if flask_env not in config_by_name:
    raise ValueError(f"Invalid value for FLASK_ENV: {flask_env}. Must be one of {list(config_by_name.keys())}")

config = config_by_name[flask_env]