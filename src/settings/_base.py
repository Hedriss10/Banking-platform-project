import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = True
    DOCS = os.getenv("DOCS_DEV")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    APPLICATION_ROOT = "/dev"
    ENV = "development"
    DEBUG = True
    PORT = os.getenv("DEV_PORT")
    DATABASE = os.getenv("DB_DEV_DATABASE")
    USERNAME = os.getenv("DB_DEV_USERNAME")
    PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DOCS = os.getenv("DOCS_DEV")
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URL")

class ProductionConfig(Config):
    APPLICATION_ROOT = "/athenas"
    ENV = "production"
    DEBUG = False
    PORT = os.getenv("PRD_PORT")
    DATABASE = os.getenv("DB_PRD_DATABASE")
    USERNAME = os.getenv("DB_PRD_USERNAME")
    PASSWORD = os.getenv("DB_PRD_PASSWORD")
    DB_HOST = os.getenv("DB_PRD_HOST")
    DB_PORT = os.getenv("DB_PRD_PORT")
    DOCS = os.getenv("DOCS_PRD")
    SQLALCHEMY_DATABASE_URI = os.getenv("PRD_DATABASE_URL")

config_by_name = {'development': DevelopmentConfig, 'production': ProductionConfig}

flask_env = os.getenv('FLASK_ENV', 'development')
if flask_env not in config_by_name:
    raise ValueError(f"Invalid value for FLASK_ENV: {flask_env}. Must be one of {list(config_by_name.keys())}")

config = config_by_name[flask_env]