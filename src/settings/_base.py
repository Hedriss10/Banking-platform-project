import os
from dotenv import load_dotenv


load_dotenv()

class Config:
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = False

class DevelopmentConfig(Config):
    APPLICATION_ROOT = "/dev"
    ENV = "development"
    DEBUG = True
    PORT = os.getenv("PORT", "5001")
    DATABASE = os.getenv("DATABASE", "maisbs")
    USERNAME = os.getenv("USERNAME", "maisbs_user")
    PASSWORD = os.getenv("PASSWORD", "maisbs@master")
    DB_HOST = os.getenv("HOST_DB", "192.168.0.242")
    DB_PORT = os.getenv("HOST_DB", "5432")
    

class ProductionConfig(Config):    
    APPLICATION_ROOT = "/athenas"
    ENV = "production"
    DEBUG = False
    PORT = os.getenv("PORT", "5002")
    DATABASE = os.getenv("DATABASE", "maisbsdv")
    USERNAME = os.getenv("USERNAME", "maisbs_user_dev")
    PASSWORD = os.getenv("PASSWORD", "maisbs@master")
    DB_HOST = os.getenv("HOST_DB", "192.168.0.242")
    DB_PORT = os.getenv("HOST_DB", "5432")

config_by_name = {'development': DevelopmentConfig, 'production': ProductionConfig}

flask_env = os.getenv('FLASK_ENV', 'development')
if flask_env not in config_by_name:
    raise ValueError(f"Invalid value for FLASK_ENV: {flask_env}. Must be one of {list(config_by_name.keys())}")

config = config_by_name[flask_env]