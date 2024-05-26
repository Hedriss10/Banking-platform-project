from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .views.user import bp_user


db = SQLAlchemy()

DB_NAME = "database.db"


def creat_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'bsconsig'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    
    app.register_blueprint(bp_user, url_prefix="/")
    
    return app