import traceback

from flask import request
from flask_cors import cross_origin
from flask_restx import Namespace, Resource

from src.core.user import UsersCore
from src.resource.swagger.factorypayloadsUser import PaylaodFactoryUser
from src.service.response import Response

# namespace
user_ns = Namespace("user", description="user")

pagination_arguments_customer = PaylaodFactoryUser.pagination_arguments_parser()
payload_add_user = PaylaodFactoryUser.add_user_payload(user_ns)
payload_edit_user = PaylaodFactoryUser.edit_user_payload(user_ns)


@user_ns.route("")
class UserResource(Resource):
    
    
    @user_ns.doc(description="Add user")
    @user_ns.expect(payload_add_user, validate=True)
    @cross_origin()
    def post(self):
        """Add user with cpf is required and unique"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))  
            
            return UsersCore(user_id=user_id).add_user(data=request.get_json())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", traceback=traceback.format_exc())

    
    @user_ns.doc(description="List Users")
    @user_ns.expect(pagination_arguments_customer, validate=True)
    @cross_origin()
    def get(self):
        """List Users"""
        
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))  
            
            return UsersCore(user_id=user_id).list_users(data=request.args.to_dict())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", traceback=traceback.format_exc())


@user_ns.route("/<int:id>")
class UserResourceManager(Resource):
    
    
    @user_ns.doc(description="Get User Filter by ID")
    @cross_origin()
    def get(self, id):
        """Get user filter by id"""
        
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))  
            
            return UsersCore(user_id=user_id).get_user(id=id)
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong",  traceback=traceback.format_exc())
    
    
    @user_ns.doc(description="Edit user filter by id")
    @user_ns.expect(payload_edit_user, validate=True)
    @cross_origin()
    def put(self, id):
        """Edit user filter by id"""
        
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))  

            return UsersCore(user_id=user_id).update_user(id=id, data=request.get_json())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", traceback=traceback.format_exc())
        
    @user_ns.doc(description="Delete user filter by id")
    @cross_origin()
    def delete(self, id):
        """Delete user filter by id"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))  
            
            return UsersCore(user_id=user_id).delete_user(id=id)
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", traceback=traceback.format_exc())
    