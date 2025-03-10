import traceback
from src.core.datacatalog import DataCatalogCore
from flask_jwt_extended import jwt_required
from flask import request
from flask_restx import Resource, Namespace, reqparse, fields
from flask_cors import cross_origin
from src.service.response import Response

pagination_arguments_customer = reqparse.RequestParser()
pagination_arguments_customer.add_argument("current_page", help="Current Page", default=1, type=int, required=False)
pagination_arguments_customer.add_argument("rows_per_page", help="Rows per Page", default=10, type=int, required=False)
pagination_arguments_customer.add_argument("order_by", help="Order By", default="", type=str, required=False)
pagination_arguments_customer.add_argument("sort_by", help="Sort By", default="", type=str, required=False)
pagination_arguments_customer.add_argument("filter_by", help="Filter By", default="", type=str, required=False)


datacatalog_ns = Namespace("datacatalog", description="Datacatalog Proposals Manager")

payload_add = datacatalog_ns.model(
    "LoanOperationAdd",
    {
        "name": fields.String(required=True, example="Margem Livre"),
    }
)

payload_add_benefit = datacatalog_ns.model(
    "BenefitAdd",
    {
        "name": fields.String(required=True, example="Por morte do trabalhador rural"),
    }
)

payload_edit_benefit = datacatalog_ns.model(
    "BenefitEdit",
    {
        "name": fields.String(required=True, example="Por morte do trabalhador rural"),
    }
)

edit_payload_loan = datacatalog_ns.model(
    "LoanOperationEdit",
    {
        "name": fields.String(required=True, example="Refin"),
    }
)

payload_add_bank = datacatalog_ns.model(
    "AddBankPayload",
    {
        "name": fields.String(required=True, example="Advanced Cc Ltda"),
        "id_bank": fields.Integer(required=True, example=102),
    },
)

edit_payload_bank = datacatalog_ns.model(
    "AddBank",
    {
        "name": fields.String(required=True, example="Advanced Cc Ltda"),
        "id_bank": fields.Integer(required=True, example=102),
    },
)


@datacatalog_ns.route("")
class ListLoanOperationResource(Resource):

    # @jwt_required()
    @datacatalog_ns.doc(description="loan Operation Add")
    @datacatalog_ns.expect(payload_add, validate=True)
    def post(self):
        """Add Loan Operation"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id")) 
            if not user_id:
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="missing_user_id",
                    exception="User ID is required but not provided in the request headers."
                )     
                    
            return DataCatalogCore(user_id=user_id).add_loan_operation(data=request.get_json())
        except Exception as e:
            return Response().response(status_code=500, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc())

    # @jwt_required()
    @datacatalog_ns.doc(description="Get All List Loan Operation")
    @datacatalog_ns.expect(pagination_arguments_customer, validate=True)    
    def get(self):
        """Get List All Loan Operation"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))      
            
            return DataCatalogCore(user_id=user_id).list_loan_operation(data=request.args.to_dict())
        except Exception as e:
            return Response().response(status_code=500, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc())

@datacatalog_ns.route("/<int:id>")
class ManageLoanOperation(Resource):
    
    # @jwt_required()
    @datacatalog_ns.doc(description="Delete Loan Operation")
    @datacatalog_ns.expect(validate=True) 
    def delete(self, id):
        """Delete Loan Operation"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))      
            
            return DataCatalogCore(user_id=user_id).delete_loan_operation(id=id)
        except Exception as e:
            return Response().response(status_code=500, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc())

@datacatalog_ns.route("/benefit/<int:id>")
class ManageBenefitOperation(Resource):
        
    # @jwt_required()
    @datacatalog_ns.doc(description="Delete Benefit")
    @datacatalog_ns.expect(validate=True) 
    def delete(self, id):
        """Delete Benefit"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))      
            
            return DataCatalogCore(user_id=user_id).delete_benefit(id=id)
        except Exception as e:
            return Response().response(status_code=500, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc())
        
@datacatalog_ns.route("/benefit")      
class ListBenefitOperation(Resource):
    
    # @jwt_required()
    @datacatalog_ns.doc(description="Benefit Add")
    @datacatalog_ns.expect(payload_add_benefit, validate=True)
    def post(self):
        """Benefit Add Operation"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))      
            
            return DataCatalogCore(user_id=user_id).add_benefit(data=request.get_json())
        except Exception as e:
            return Response().response(status_code=500, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc())
    
    @datacatalog_ns.doc(description="Get All List Benefit")
    @datacatalog_ns.expect(pagination_arguments_customer, validate=True)    
    def get(self):
        """Get List All Benefit"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))      
            
            return DataCatalogCore(user_id=user_id).list_benefit(data=request.args.to_dict())
        
        except Exception as e:
            return Response().response(status_code=500, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc())

@datacatalog_ns.route("/bank")
class ListBankOperation(Resource):
    
    # @jwt_required()
    @datacatalog_ns.doc(description="Bank Add")
    @datacatalog_ns.expect(payload_add_bank, validate=True)
    def post(self):
        """Bank Add Operation"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))      
            
            return DataCatalogCore(user_id=user_id).add_bank(data=request.get_json())

        except Exception as e:
            return Response().response(status_code=500, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc())
    
    # @jwt_required()
    @datacatalog_ns.doc(description="Get All List Bank")
    @datacatalog_ns.expect(pagination_arguments_customer, validate=True)    
    def get(self):
        """Get List All Bank"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))      
            
            return DataCatalogCore(user_id=user_id).list_bank(data=request.args.to_dict())
        except Exception as e:
            return Response().response(status_code=500, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc())
    
@datacatalog_ns.route("/bank/<int:id>")
class ManageBankOperation(Resource):
        
    # @jwt_required()
    @datacatalog_ns.doc(description="Delete Bank")
    @datacatalog_ns.expect(validate=True) 
    def delete(self, id):
        """Delete Bank"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))      
            
            return DataCatalogCore(user_id=user_id).delete_bank(id=id)
        except Exception as e:
            return Response().response(status_code=500, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc())
