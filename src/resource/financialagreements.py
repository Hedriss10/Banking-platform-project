import traceback
from flask_jwt_extended import jwt_required
from flask import request
from flask_restx import Resource, Namespace
from flask_cors import cross_origin
from src.core.financialagreements import FinancialAgreementsCore
from src.service.response import Response
from src.resource.swagger.factorypayloadsFinance import FactoryPayloadsFinancialAgreements
from flask_jwt_extended import jwt_required


financial_agreements_ns = Namespace("financialagreements", description="Manage Financial Agreements")
pagination_customer = FactoryPayloadsFinancialAgreements.pagination_arguments_parser()
paylaod_add_financialagreements =  FactoryPayloadsFinancialAgreements.paylaod_add_financialagreements(financial_agreements_ns)
paylaod_edit_financialagreements = FactoryPayloadsFinancialAgreements.paylaod_edit_financialagreements(financial_agreements_ns)

@financial_agreements_ns.route("")
class BankerResourceRegister(Resource):
    
    # @jwt_required()
    @financial_agreements_ns.doc(description="Financial Agreements")
    @financial_agreements_ns.expect(paylaod_add_financialagreements, validate=True)
    @cross_origin()
    def post(self):
        """Add financial_agreements, name financial_agreements is required and unique"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))      
            return FinancialAgreementsCore(user_id=user_id).add_financial_agreements(data=request.get_json())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc())
        
    # @jwt_required()
    @financial_agreements_ns.doc(description="List financial agreements")
    @financial_agreements_ns.expect(pagination_customer, validate=True)
    @cross_origin()  
    def get(self):
        """List all financial_agreements"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))      
            return FinancialAgreementsCore(user_id=user_id).list_financial_agreements(data=request.args.to_dict())

        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc())


@financial_agreements_ns.route("/<int:id>")
class BankerResourceFilterById(Resource):

    # @jwt_required()
    @financial_agreements_ns.doc(description="Get financial agreements Filter by id")
    @cross_origin()
    def get(self, id):
        """Get filter financial_agreements by ID"""
        
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))  
            
            return FinancialAgreementsCore(user_id=user_id).get_financial_agreements(id=id)
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))
    
    # @jwt_required()
    @financial_agreements_ns.doc(description="Edit financial agreements filter by id")
    @financial_agreements_ns.expect(paylaod_edit_financialagreements, validate=True)
    @cross_origin()
    def put(self, id):
        """Edit filter financial_agreements by ID"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))  
            
            return FinancialAgreementsCore(user_id=user_id).update_financial_agreements(id=id, data=request.get_json())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))
    
    
    # @jwt_required()
    @financial_agreements_ns.doc(description="Get financial agreements Filter by ID")
    @cross_origin()
    def delete(self, id):
        """Delete filter financial_agreements by ID"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))  
            
            return FinancialAgreementsCore(user_id=user_id).delete_financial_agreements(id=id)
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))