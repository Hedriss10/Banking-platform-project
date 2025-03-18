import traceback
from flask import request
from flask_restx import Resource, Namespace
from flask_cors import cross_origin
from src.core.users import UsersCore
from src.service.response import Response
from src.resource.swagger.factorypayloadsUser import PaylaodFactoryUser

# namespace
users_ns = Namespace("user", description="user")

pagination_arguments_customer = PaylaodFactoryUser.pagination_arguments_parser()
payload_add_user = PaylaodFactoryUser.add_user_payload(users_ns)
payload_edit_user = PaylaodFactoryUser.edit_user_payload(users_ns)
# resource apis

@users_ns.route("")
class UserResource(Resource):
    
    
    @users_ns.doc(description="Add user")
    @users_ns.expect(payload_add_user, validate=True)
    @cross_origin()
    def post(self):
        """Add user with cpf is required and unique"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))  
            
            return UsersCore(user_id=user_id).add_user(data=request.get_json())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", traceback=traceback.format_exc())

    
    @users_ns.doc(description="List Users")
    @users_ns.expect(pagination_arguments_customer, validate=True)
    @cross_origin()
    def get(self):
        """List Users"""
        
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))  
            
            return UsersCore(user_id=user_id).list_users(data=request.args.to_dict())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", traceback=traceback.format_exc())


@users_ns.route("/<int:id>")
class UserResourceManager(Resource):
    
    
    @users_ns.doc(description="Get User Filter by ID")
    @cross_origin()
    def get(self, id):
        """Get user filter by id"""
        
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))  
            
            return UsersCore(user_id=user_id).get_user(id=id)
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong",  traceback=traceback.format_exc())
    
    
    @users_ns.doc(description="Edit user filter by id")
    @users_ns.expect(payload_edit_user, validate=True)
    @cross_origin()
    def put(self, id):
        """Edit user filter by id"""
        
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))  

            return UsersCore(user_id=user_id).update_user(id=id, data=request.get_json())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", traceback=traceback.format_exc())
        
    
    @users_ns.doc(description="Delete user filter by id")
    @cross_origin()
    def delete(self, id):
        """Delete user filter by id"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))  
            
            return UsersCore(user_id=user_id).delete_user(id=id)
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", traceback=traceback.format_exc())
    