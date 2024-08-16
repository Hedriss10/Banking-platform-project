from decouple import config

class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = config('DATABASE_URL', default='sqlite:///development.db')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = config('DATABASE_URL', default='sqlite:///production.db')


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    DEBUG_TB_ENABLED = True
    PORT_HOST = 8000
    SQLALCHEMY_DATABASE_URI = config('DEV_DATABASE_URL', default='sqlite:///db.sqlite')
    
