import traceback

from flask import request
from flask_cors import cross_origin
from flask_restx import Namespace, Resource, fields, reqparse

from src.core.operational import OperationalCore
from src.service.response import Response

# pagination arguments customer
pagination_arguments_customer = reqparse.RequestParser()
pagination_arguments_customer.add_argument(
    "current_page", help="Current Page", default=1, type=int, required=False
)
pagination_arguments_customer.add_argument(
    "rows_per_page", help="Rows per Page", default=10, type=int, required=False
)
pagination_arguments_customer.add_argument(
    "order_by", help="Order By", default="", type=str, required=False
)
pagination_arguments_customer.add_argument(
    "sort_by", help="Sort By", default="", type=str, required=False
)
pagination_arguments_customer.add_argument(
    "filter_by", help="Filter By", default="", type=str, required=False
)


operatinal_ns = Namespace("operational", description="Manage Operational")


payload_operational = operatinal_ns.model(
    "TypingProposal",
    {
        "aguardando_digitacao": fields.Boolean(required=False, example=False),
        "pendente_digitacao": fields.Boolean(required=False, example=False),
        "contrato_em_digitacao": fields.Boolean(required=False, example=False),
        "aceite_feito_analise_banco": fields.Boolean(
            required=False, example=False
        ),
        "contrato_pendente_banco": fields.Boolean(
            required=False, example=False
        ),
        "aguardando_pagamento": fields.Boolean(required=False, example=False),
        "contrato_pago": fields.Boolean(required=False, example=True),
        "description": fields.String(
            required=False, example="Description of proposal"
        ),
        "number_proposal": fields.Integer(required=False, example=40028922),
    },
)


@operatinal_ns.route("/<int:proposal_id>")
class ListProposalResource(Resource):
    # # @jwt_required()
    @operatinal_ns.doc(description="Add typing proposal with number")
    @operatinal_ns.expect(payload_operational)
    @cross_origin()
    def post(self, proposal_id: int):
        """Add Typing proposal with number"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            if not user_id:
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="missing_user_id",
                    exception="User ID is required but not provided in the request headers.",
                )

            return OperationalCore(user_id=user_id).typing_proposal(
                proposal_id=proposal_id, data=request.get_json()
            )
        except Exception as e:
            return Response().response(
                status_code=500,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(),
            )


@operatinal_ns.route("/count")
class CountProposalResource(Resource):
    # @jwt_required()
    @operatinal_ns.doc(description="Count Proposal Typing Pendant")
    @cross_origin()
    def get(self):
        """Count Proposal typing pendant"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            if not user_id:
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="missing_user_id",
                    exception="User ID is required but not provided in the request headers.",
                )

            return OperationalCore(user_id=user_id).count_proposal()
        except Exception as e:
            return Response().response(
                status_code=500,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(),
            )


@operatinal_ns.route("/proposal")
class ListProposalResource(Resource):
    # # @jwt_required()
    @operatinal_ns.doc(description="List proposal")
    @operatinal_ns.expect(pagination_arguments_customer, validate=True)
    @cross_origin()
    def get(self):
        """List proposal order by created_at"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            if not user_id:
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="missing_user_id",
                    exception="User ID is required but not provided in the request headers.",
                )

            return OperationalCore(user_id=user_id).list_proposal(
                data=request.args.to_dict()
            )
        except Exception as e:
            return Response().response(
                status_code=500,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(),
            )


@operatinal_ns.route("/proposal/history/<int:id>")
class ListProposalHistoryResource(Resource):
    # @jwt_required()
    @operatinal_ns.doc(description="History proposals filter by id proposal")
    @operatinal_ns.expect(pagination_arguments_customer, validate=True)
    @cross_origin()
    def get(self, id):
        """History proposals filter by id proposal"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            if not user_id:
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="missing_user_id",
                    exception="User ID is required but not provided in the request headers.",
                )

            return OperationalCore(user_id=user_id).history_proposal(
                proposal_id=id, data=request.args.to_dict()
            )
        except Exception as e:
            return Response().response(
                status_code=500,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(),
            )


@operatinal_ns.route("/proposal/details/<int:id>")
class ListProposalDetailsResource(Resource):
    # @jwt_required()
    @operatinal_ns.doc(description="Details proposals filter by id proposal")
    @cross_origin()
    def get(self, id):
        """Details proposals filter by id proposal"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            if not user_id:
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="missing_user_id",
                    exception="User ID is required but not provided in the request headers.",
                )

            return OperationalCore(user_id=user_id).details_proposal(
                proposal_id=id
            )
        except Exception as e:
            return Response().response(
                status_code=500,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(),
            )
