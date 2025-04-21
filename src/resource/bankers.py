import traceback

from flask import request
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource

from src.core.finance import BankersCore, FinancialAgreementsCore
from src.resource.swagger.factorypayloadsFinance import FactoryPayloadsBankers, FactoryPayloadsFinancialAgreements
from src.service.response import Response

bankers_ns = Namespace("bankers", description="Manage Bankers")


pagination_arguments_customer = FactoryPayloadsBankers.pagination_arguments_parser()
bankers_add = FactoryPayloadsBankers.add_payload_banker(bankers_ns)
bankers_put = FactoryPayloadsBankers.edit_payload_banker(bankers_ns)
paylaod_add_financialagreements =  FactoryPayloadsFinancialAgreements.paylaod_add_financialagreements(bankers_ns)
paylaod_edit_financialagreements = FactoryPayloadsFinancialAgreements.paylaod_edit_financialagreements(bankers_ns)


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
            return BankersCore(user_id=user_id).add_banker(data=request.get_json())
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
            return BankersCore(user_id=user_id).list_bankers(data=request.args.to_dict())

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
            
            return BankersCore(user_id=user_id).get_banker(id=id)
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
            
            return BankersCore(user_id=user_id).update_banker(id=id, data=request.get_json())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))
    
    
    # @jwt_required()
    @bankers_ns.doc(description="Get Banker Filter by ID")
    @cross_origin()
    def delete(self, id):
        """Delete filter banker by ID"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))

            return BankersCore(user_id=user_id).delete_banker(id=id)
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))
        

@bankers_ns.route("/financial_agreements")
class FinancialAgreeementsResource(Resource):
    @bankers_ns.doc(description="Financial Agreements")
    @bankers_ns.expect(paylaod_add_financialagreements, validate=True)
    @cross_origin()
    def post(self):
        """Add financial_agreements, name financial_agreements is required and unique"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))      
            return FinancialAgreementsCore(user_id=user_id).add_financial_agreements(data=request.get_json())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc())

@bankers_ns.route("/financial_agreements/<int:id>")
class FinancialAgreementsResourceFilterById(Resource):
    @bankers_ns.doc(description="Edit financial agreements filter by id")
    @bankers_ns.expect(paylaod_edit_financialagreements, validate=True)
    @cross_origin()
    def put(self, id):
        """Edit filter financial_agreements by ID"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))  
            
            return FinancialAgreementsCore(user_id=user_id).update_financial_agreements(id=id, data=request.get_json())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))
    
    @bankers_ns.doc(description="Get financial agreements Filter by ID")
    @cross_origin()
    def delete(self, id):
        """Delete filter financial_agreements by ID"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))  
            
            return FinancialAgreementsCore(user_id=user_id).delete_financial_agreements(id=id)
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))