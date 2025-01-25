# src/external.py
from flask import Flask, request
from flask_cors import CORS
from flask_restx import Api
from os import environ
from flask_jwt_extended import JWTManager
from src.settings._base import config, flask_env


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
    
    @app.before_request
    def decompress():
        if request.data != b"" and flask_env != "development" and flask_env != "production":
            request.data = Magicrypt().decrypt(request.data)
            request._cached_data = request.data

    @app.after_request
    def compress(response):
        if flask_env != "development" and flask_env != "production":
            response.data = Magicrypt().encrypt(response.data)
        return response 

    # Namespaces registration
    api.add_namespace(users_ns)
    api.add_namespace(login_ns)

    return app