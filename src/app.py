# src/external.py
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restx import Api

from src.db.database import db
from src.resource.bankerfinance import bankers_ns
from src.resource.dashboard import dashboard_ns
from src.resource.datacatalog import datacatalog_ns
from src.resource.flag import flag_ns
from src.resource.hourspoint import hourspoint_ns
from src.resource.login import login_ns
from src.resource.operational import operatinal_ns
from src.resource.payment import payment_ns
from src.resource.proposal import proposal_ns
from src.resource.report import report_ns
from src.resource.role import roles_ns
from src.resource.rooms import rooms_ns
from src.resource.statistics import statistics_ns
from src.resource.table import tables_ns
from src.resource.user import user_ns
from src.settings._base import config

# refractor

def create_app():
    app = Flask(__name__, static_folder="static")
    app.config.from_object(config)
    
    db.init_app(app) # init database
    
    authorizations = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
        }
    }

    api = Api(
        app,
        prefix=f"/{app.config['APPLICATION_ROOT']}",
        doc=f"/{app.config["DOCS"]}",
        authorizations=authorizations,
        security="Bearer Auth",
        version="3.0",
        title="Athenas Backend API micro serviços",
        description="Backend Athenas.",
    )
    app.config["CORS_HEADERS"] = "Content-Type"
    CORS(app, resources={r"/*": {"origins": "*"}, r"/static/*": {"origins": "*"}})

    app.config["JWT_SECRET_KEY"] = "bsconsig"
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"
    # app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)

    jwt = JWTManager(app)
    
    # Namespaces registration
    api.add_namespace(user_ns)
    api.add_namespace(login_ns)
    api.add_namespace(datacatalog_ns)
    api.add_namespace(hourspoint_ns)
    api.add_namespace(bankers_ns)
    api.add_namespace(operatinal_ns)
    api.add_namespace(proposal_ns)
    api.add_namespace(report_ns)
    api.add_namespace(roles_ns)
    api.add_namespace(rooms_ns)
    api.add_namespace(statistics_ns)
    api.add_namespace(tables_ns)
    api.add_namespace(flag_ns)
    api.add_namespace(payment_ns)
    api.add_namespace(dashboard_ns)

    return app