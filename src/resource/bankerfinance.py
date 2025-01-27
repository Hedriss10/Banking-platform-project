import traceback
from flask_jwt_extended import jwt_required
from flask import request
from flask_restx import Resource, Namespace
from flask_cors import cross_origin
from src.core.bankerfinance import BankerFinanceCore
from src.service.response import Response
from src.resource.swagger.factorypayloadsFinance import FactoryPayloadsFinancialAgreements, FactoryPayloadsBankers

bankers_ns = Namespace("bankers", description="Manage Bankers")


pagination_arguments_customer = FactoryPayloadsBankers.pagination_arguments_parser()
bankers_add = FactoryPayloadsBankers.add_payload_banker(bankers_ns)
bankers_put = FactoryPayloadsBankers.edit_payload_banker(bankers_ns)


@bankers_ns.route("")
class BankerResourceRegister(Resource):
    
    # @jwt_required()
    @bankers_ns.doc(description="Add Banker")
    @bankers_ns.expect(bankers_add, validate=True)
    @cross_origin()
    def post(self):
        """Add banker, name banker is required and unique"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))   
            return BankerFinanceCore(user_id=user_id).add_banker(data=request.get_json())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))
        
    # # @jwt_required()
    @bankers_ns.doc(description="List Banker")
    @bankers_ns.expect(pagination_arguments_customer, validate=True)
    @cross_origin()  
    def get(self):
        """List all bankers"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return BankerFinanceCore(user_id=user_id).list_bankers(data=request.args.to_dict())

        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))


@bankers_ns.route("/<int:id>")
class BankerResourceFilterById(Resource):

    # # @jwt_required()
    @bankers_ns.doc(description="Get Banker Filter by ID")
    @cross_origin()
    def get(self, id):
        """Get filter banker by ID"""
        
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            
            return BankerFinanceCore(user_id=user_id).get_banker(id=id)
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))
    
    # @jwt_required()
    @bankers_ns.doc(description="Get Banker Filter by ID")
    @bankers_ns.expect(bankers_put, validate=True)
    @cross_origin()
    def put(self, id):
        """Edit filter banker by ID"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            
            return BankerFinanceCore(user_id=user_id).update_banker(id=id, data=request.get_json())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))
    
    
    # @jwt_required()
    @bankers_ns.doc(description="Get Banker Filter by ID")
    @cross_origin()
    def delete(self, id):
        """Delete filter banker by ID"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))

            return BankerFinanceCore(user_id=user_id).delete_banker(id=id)
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))