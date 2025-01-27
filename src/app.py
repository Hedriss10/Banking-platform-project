# src/external.py
from flask import Flask, request
from flask_cors import CORS
from flask_restx import Api
from os import environ
from flask_jwt_extended import JWTManager
from src.settings._base import config, flask_env

from src.resource.users import users_ns
from src.resource.login import login_ns
from src.resource.datacatalog import datacatalog_ns
from src.resource.hourspoint import hourspoint_ns
from src.resource.financialagreements import financial_agreements_ns
from src.resource.bankerfinance import bankers_ns
from src.resource.operational import operatinal_ns
from src.resource.proposal import proposal_ns
from src.resource.reportfinance import report_ns
from src.resource.role import roles_ns
from src.resource.rooms import rooms_ns
from src.resource.statistics import profit_ns
from src.resource.tablesfinance import tables_finance_ns
from src.resource.token import token_ns


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    
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
        doc="/doc",
        authorizations=authorizations,
        security="Bearer Auth",
        version="2.0",
        title="Athenas Users",
        description="Documentação completa do users e login.",
    )

    cors = CORS(app)
    app.config["CORS_HEADERS"] = "Content-Type"
    CORS(app, resources={r"/*": {"origins": "*"}})

    app.config["JWT_SECRET_KEY"] = "bsconsig"
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"
    # app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)

    jwt = JWTManager(app)
    
    # Namespaces registration
    api.add_namespace(users_ns)
    api.add_namespace(login_ns)
    api.add_namespace(datacatalog_ns)
    api.add_namespace(hourspoint_ns)
    api.add_namespace(financial_agreements_ns)
    api.add_namespace(bankers_ns)
    api.add_namespace(operatinal_ns)
    api.add_namespace(proposal_ns)
    api.add_namespace(report_ns)
    api.add_namespace(roles_ns)
    api.add_namespace(rooms_ns)
    api.add_namespace(profit_ns)
    api.add_namespace(tables_finance_ns)
    api.add_namespace(token_ns)

    return app