from flask import Flask, render_template
from src.settings._base import config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from src.auth.auth import UserAuth


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)    
    jwt = JWTManager(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login" 
    
    db.init_app(app)
    
    from src.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        user = User.query.get(int(user_id))
        if user:
            return UserAuth(
                id=user.id,
                username=user.username,
                email=user.email,
                password=user.password,
                role=user.role,
                session_token=user.session_token,
                is_acctive=user.is_acctive,
                is_block=user.is_block,
                is_deleted=user.is_deleted,
            )
        return None

    from src.auth.login import bp_auth
    from src.routes.overview import bp_overview
    
    app.register_blueprint(bp_auth, url_prefix="/")
    app.register_blueprint(bp_overview, url_prefix="/")
 
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('partials/404.html'), 404
    
    return app
