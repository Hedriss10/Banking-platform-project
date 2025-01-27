import traceback
from flask import request
from flask_restx import Resource, Namespace
from flask_cors import cross_origin
from src.core.token import CoreToken
from src.service.response import Response


token_ns = Namespace("token", description="Manager token",)


@token_ns.route("/<int:id>")
class TokenManager(Resource):
    
    # @jwt_required()
    @token_ns.doc(description="Get filter token")
    @cross_origin()
    def get(self, id):
        """Get filter token"""
        
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            
            return CoreToken(user_id=user_id).get_token(id=id)
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))