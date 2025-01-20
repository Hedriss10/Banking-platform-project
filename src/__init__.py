from flask import Flask, render_template
from src.settings._base import config
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from models.user import User


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    
    jwt = JWTManager(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login" 
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from src.auth.login import bp_auth
    from src.routes.overview import bp_overview
    
    app.register_blueprint(bp_auth, url_prefix="/")
    app.register_blueprint(bp_overview, url_prefix="/")
 
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('partials/404.html'), 404
    
    return app
