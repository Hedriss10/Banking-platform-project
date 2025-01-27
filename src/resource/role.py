import traceback
from flask import request
from flask_restx import Namespace, Resource
from flask_cors import cross_origin
from src.core.role import RoleCore
from src.service.response import Response
from src.resource.swagger.factorypayloadsOperational import PayloadFactoryRole


roles_ns = Namespace("role", description="Manage Role")

pagination_arguments_customer = PayloadFactoryRole.pagination_arguments_parser()
paylaod_role_ns = PayloadFactoryRole.add_payload_role(roles_ns)


@roles_ns.route("")
class RoleManager(Resource):

    @roles_ns.doc(description="Add role")
    @roles_ns.expect(paylaod_role_ns, validate=True)
    def post(self):
        """Add role"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return RoleCore(user_id=user_id).add_role(data=request.get_json())

        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))

    @roles_ns.doc(description="List role")
    @roles_ns.expect(pagination_arguments_customer, validate=True)
    @cross_origin()
    def get(self):
        """List all role"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return RoleCore(user_id=user_id).list_role(data=request.args.to_dict())

        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))
        
@roles_ns.route("/<int:id>")    
class RoleManagerId(Resource):
    
    @roles_ns.doc(description="Delete role")
    @roles_ns.expect(validate=True)
    @cross_origin()
    def delete(self, id):
        """Delete role"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return RoleCore(user_id=user_id).delete_role(id=id)

        except Exception as e:
            print(e)
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))