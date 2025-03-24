import traceback
from flask_jwt_extended import jwt_required
from flask import request
from flask_restx import Resource, Namespace
from flask_cors import cross_origin
from src.core.payment import PaymentsCore
from src.service.response import Response
from src.resource.swagger.payment import PaymentsFactoryPayloads


# pagination
pagination_arguments_payment = PaymentsFactoryPayloads.pagination_args_parse()
pagination_customer_payments_sellers = PaymentsFactoryPayloads.pagination_list_payments_sellers()

payment_ns = Namespace("payment", description="Manage Payments")

payload_add_payments = PaymentsFactoryPayloads.payload_add_payments(payment_ns)
payload_delete_payments = PaymentsFactoryPayloads.payload_delete_payments(payment_ns)

@payment_ns.route("")
class PaymentResource(Resource):
    
    # @jwt_required()
    @payment_ns.doc(description="List payments processing")
    @payment_ns.expect(pagination_arguments_payment, validate=True)
    @cross_origin()
    def get(self):
        """List payments processing"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return PaymentsCore(user_id=user_id).list_processing_payments(data=request.args.to_dict())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))

    # @jwt_required()
    @payment_ns.doc(description="Add process payments")
    @payment_ns.expect(payload_add_payments, validate=True)
    @cross_origin()
    def post(self):
        """Add process payments with id flag and ids users or unique id"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return PaymentsCore(user_id=user_id).processing_payments(data=request.get_json())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))

    @payment_ns.doc(description="Delete process payments")
    @payment_ns.expect(payload_delete_payments, validate=True)
    @cross_origin()
    def delete(self):
        """Delete process payments"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return PaymentsCore(user_id=user_id).delete_processing_payment(data=request.get_json())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))

@payment_ns.route("/sellers")
class ListSellersResource(Resource):

    # @jwt_required()
    @payment_ns.doc(description="list of sellers that contain a paid proposal, parameter has report and contains a paid proposal but is not in the report")
    @payment_ns.expect(pagination_customer_payments_sellers, validate=True)
    @cross_origin()
    def get(self):
        """list of sellers that contain a paid proposal, parameter has report and contains a paid proposal but is not in the report"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))

            return PaymentsCore(user_id=user_id).list_sellers(data=request.args.to_dict())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))