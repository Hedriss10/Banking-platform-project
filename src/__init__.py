from flask import Flask, render_template
from flask_login import LoginManager, current_user
from src.settings._base import config
from flask import flash, redirect, url_for
from functools import wraps

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = "danger"
    login_manager.init_app(app)

    from src.routes.user import bp_user
    from src.routes.overview import bp_overview
    from src.auth.user_manager import bp_auth
    from src.routes.fynance import bp_fynance
    from src.routes.proposal import bp_proposal
    from src.routes.admin import bp_admin
    from src.routes.rooms import bp_room
    from src.routes.operational import bp_operational

    app.register_blueprint(bp_user, url_prefix="/")
    app.register_blueprint(bp_overview, url_prefix="/")
    app.register_blueprint(bp_auth, url_prefix="/")
    app.register_blueprint(bp_fynance, url_prefix="/")
    app.register_blueprint(bp_proposal, url_prefix="/")
    app.register_blueprint(bp_admin, url_prefix="/")
    app.register_blueprint(bp_room, url_prefix="/")
    app.register_blueprint(bp_operational, url_prefix="/")
    
    from src.models.bsmodels import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('partials/404.html'), 404
    
    return app

def check_session_token(f):
    from src.models.bsmodels import User
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = User.query.get(current_user.id)  # Obtém o usuário do banco de dados
        if user.session_token != current_user.session_token:            
            flash('Sessão inválida. Faça login novamente.')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
