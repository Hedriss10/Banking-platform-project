from flask import Flask, render_template
from src.settings._base import config
from src.core.login import LoginCore
from src.core.user import UsersCore
from flask import flash, redirect, url_for
from functools import wraps

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    

    from src.auth.login import bp_auth
    app.register_blueprint(bp_auth, url_prefix="/")

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('partials/404.html'), 404
    
    return app
