import os 
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

from .config import (DevelopmentConfig, 
                     ProductionConfig, TestingConfig)  

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_class=DevelopmentConfig):  
    app = Flask(__name__)
    
    env_config = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }
    
    config_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(env_config.get(config_name, DevelopmentConfig))

    
    db.init_app(app)
    migrate.init_app(app, db)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = "danger"
    login_manager.init_app(app)
    
    
    from .views.user import bp_user
    from .views.overview import bp_overview
    from .auth.userManager import bp_auth
    from .views.hourpoint import bp_point_hour
    from .views.fynance import bp_fynance
    
    app.register_blueprint(bp_user, url_prefix="/")
    app.register_blueprint(bp_overview, url_prefix="/")
    app.register_blueprint(bp_auth, url_prefix="/")
    app.register_blueprint(bp_point_hour, url_prefix="/")
    app.register_blueprint(bp_fynance, url_prefix="/")
    
    from .models.user import User
    from .models.hourpoint import Point, VocationBs
    from .models.fynance import Banker, FinancialAgreement, TablesFinance, RankFlat
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return app