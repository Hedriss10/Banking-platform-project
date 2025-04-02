import traceback

from flask import request
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, fields

from src.core.login import LoginCore
from src.resource.swagger.factorypayloadsLogin import PayloadFactoryLogin
from src.service.response import Response

login_ns = Namespace("login", description="login")
login_payload = PayloadFactoryLogin.login_platform_payload(login_ns)
rest_password_payload = PayloadFactoryLogin.reset_login_paylaod(login_ns)
rest_password_master_payload = PayloadFactoryLogin.reset_master_password(login_ns)

@login_ns.route("")
class LoginResource(Resource):
    
    @login_ns.doc(description="Get User Login")
    @login_ns.expect(login_payload, validate=True)
    @cross_origin()
    def post(self):
        """Get user login"""
        try:
            return LoginCore().get_login(request.get_json())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc())
    

@login_ns.route("/reset-master")
class ResetPasswordResourceMaster(Resource):
    
    # @jwt_required()
    @login_ns.doc(description="Reset Password Master")
    @login_ns.expect(rest_password_master_payload, validate=True)
    @cross_origin()
    def post(self):
        """Request resert password master"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))  
            
            return LoginCore(user_id=user_id).reset_password_authorization(user_id=user_id, data=request.get_json())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc())
        