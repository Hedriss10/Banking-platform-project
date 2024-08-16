import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from src.config import DevelopmentConfig, ProductionConfig, TestingConfig


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(24)

    env_config = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }
    
    config_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(env_config.get(config_name, DevelopmentConfig))

    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    db.init_app(app)
    migrate.init_app(app, db)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = "danger"
    login_manager.init_app(app)
    
    from src.views.user import bp_user
    from src.views.overview import bp_overview
    from src.auth.userManager import bp_auth
    from src.views.hourpoint import bp_point_hour
    from src.views.fynance import bp_fynance
    from src.views.proposal import bp_proposal
    from src.views.admin import bp_admin
    
    app.register_blueprint(bp_user, url_prefix="/users")
    app.register_blueprint(bp_overview, url_prefix="/")
    app.register_blueprint(bp_auth, url_prefix="/")
    app.register_blueprint(bp_point_hour, url_prefix="/")
    app.register_blueprint(bp_fynance, url_prefix="/")
    app.register_blueprint(bp_proposal, url_prefix="/")
    app.register_blueprint(bp_admin, url_prefix="/")
    
    
    from src.models.user import User
    from src.models.hourpoint import Point, VocationBs
    from src.models.fynance import Banker, FinancialAgreement, TablesFinance, RankFlat
    from src.models.proposal import UserProposal
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return app
