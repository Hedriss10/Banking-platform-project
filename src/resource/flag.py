import traceback

from flask import request
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, fields, reqparse

from src.core.flag import FlagsCore
from src.resource.swagger.flag import FlagsFactoryPayloads
from src.service.response import Response

# pagination
paginantion_arguments_flags = FlagsFactoryPayloads().pagination_arguments_parser()

# namespace
flag_ns = Namespace("flags", description="Manage flags")

payload_add_flags = FlagsFactoryPayloads().payload_add_flags(flag_ns)
payload_delete_ids = FlagsFactoryPayloads().payload_delete_flags(flag_ns)

@flag_ns.route("")
class FlagsResourceManage(Resource):

    # @jwt_required()
    @flag_ns.doc(description="list flags")
    @flag_ns.expect(paginantion_arguments_flags, validate=True)
    @cross_origin()
    def get(self):
        """List flags"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))

            return FlagsCore(user_id=user_id).list_flags(data=request.args.to_dict())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))

    # @jwt_required()
    @flag_ns.doc(description="Add flags")
    @flag_ns.expect(payload_add_flags, validate=True)
    @cross_origin()
    def post(self):
        """Add flags"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return FlagsCore(user_id=user_id).add_flags(data=request.get_json())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))

    # @jwt_required()
    @flag_ns.doc(description="Delete flags")
    @flag_ns.expect(payload_delete_ids, validate=True)
    @cross_origin()
    def delete(self):
        """Delete flags"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return FlagsCore(user_id=user_id).delete_flag(data=request.get_json())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))