from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# init plugins
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)    
    app.config['SECRET_KEY'] = 'bsconsig'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///database.db'
    
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    login_manager.login_view = 'user.login'
    
    from .views.user import bp_user
    from .views.overview import bp_overview
    
    app.register_blueprint(bp_user, url_prefix="/")
    app.register_blueprint(bp_overview, url_prefix="/")
    
    from .models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return app
