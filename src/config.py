from decouple import config

class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = config('SECRET_KEY', default='bs-consig')
    SQLALCHEMY_DATABASE_URI = config('DATABASE_URL').replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BCRYPT_LOG_ROUNDS = 13
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    DEBUG_TB_ENABLED = True
    PORT_HOST = 8000
    SQLALCHEMY_DATABASE_URI = config('DEV_DATABASE_URL', default='sqlite:///db.sqlite')
    
class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testdb.sqlite'
    BCRYPT_LOG_ROUNDS = 1

class ProductionConfig(Config):
    DEBUG = False
    DEBUG_TB_ENABLED = False
