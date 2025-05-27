import traceback

from flask import request
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource

from src.core.payment import PaymentsCore, PaymentsServiceProvided
from src.resource.swagger.payment import PaymentsFactoryPayloads
from src.service.response import Response

# pagination
pagination_arguments_payment = PaymentsFactoryPayloads.pagination_args_parse()
pagination_customer_payments_sellers = PaymentsFactoryPayloads.pagination_list_payments_sellers()

payment_ns = Namespace("payment", description="Manage Payments")

payload_add_payments = PaymentsFactoryPayloads.payload_add_payments(payment_ns)
payload_delete_payments = PaymentsFactoryPayloads.payload_delete_payments(payment_ns)
payload_add_service_provided = PaymentsFactoryPayloads.payload_add_service_provided(payment_ns)
payload_delete_service_provided = PaymentsFactoryPayloads.payload_delete_service_provided(payment_ns)


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
            return PaymentsCore(user_id=user_id).list_payments(data=request.args.to_dict())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))

    # @jwt_required()
    @payment_ns.doc(description="Add process payments")
    # @payment_ns.expect(payload_add_payments, validate=True)
    @cross_origin()
    def post(self):
        """Add processing payments for with id users"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return PaymentsCore(user_id=user_id).add_payment(data=request.get_json())
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

@payment_ns.route("/proposal")
class ListSellersResource(Resource):

    # @jwt_required()
    @payment_ns.doc(description="list of sellers that contain a paid proposal, parameter has report and contains a paid proposal but is not in the report")
    @payment_ns.expect(pagination_customer_payments_sellers, validate=True)
    @cross_origin()
    def get(self):
        """list proposal the for payments sellers reports"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))

            return PaymentsCore(user_id=user_id).list_proposal(data=request.args.to_dict())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))


@payment_ns.route("/service-provided")
class ManagerPaymentServiceProvided(Resource):
    
    # @jwt_required()
    @payment_ns.doc(description="Add payments service provided")
    @payment_ns.expect(payload_add_service_provided, validate=True)
    @cross_origin()
    def post(self):
        """Add payments service provided"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return PaymentsServiceProvided(user_id=user_id).add_payments_service_provided(data=request.get_json())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))
    
    # @jwt_required()
    @payment_ns.doc(description="list payments service provided")
    @payment_ns.expect(pagination_arguments_payment, validate=True)
    def get(self):
        """List payments processing"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return PaymentsServiceProvided(user_id=user_id).list_payments_service_provided(request.args.to_dict())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))
    
    @payment_ns.doc(description="Delete service provided")
    @payment_ns.expect(payload_delete_service_provided, validate=True)    
    def delete(self):
        """Delete paymenyts provided"""
        
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return PaymentsServiceProvided(user_id=user_id).delete_payments_service_provided(data=request.get_json())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))