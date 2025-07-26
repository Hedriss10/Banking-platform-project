import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()


class Config:
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = True
    DOCS = os.getenv("DOCS_DEV")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    password = quote_plus("maisbs@master")
    APPLICATION_ROOT = "/dev"
    ENV = "development"
    PORT = 5002
    DOCS = "/docs"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"{os.getenv('SQLALCHEMY_DATABASE_URI')}"


class ProductionConfig(Config):
    APPLICATION_ROOT = "/athenas"
    ENV = "production"
    PORT = 5002
    DOCS = "/docs"
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = f"{os.getenv('SQLALCHEMY_DATABASE_URI')}"


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}

flask_env = os.getenv("FLASK_ENV", "development")
if flask_env not in config_by_name:
    raise ValueError(
        f"Invalid value for FLASK_ENV: {flask_env}. Must be one of {list(config_by_name.keys())}"
    )
