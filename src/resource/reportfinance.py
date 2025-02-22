import traceback
from flask_jwt_extended import jwt_required
from flask import request
from flask_restx import Resource, Namespace, fields, reqparse
from flask_cors import cross_origin
from src.core.reportfinance import ReportCore
from src.service.response import Response
from werkzeug.datastructures import FileStorage

pagination_arguments_customer = reqparse.RequestParser()
pagination_arguments_customer.add_argument("current_page", help="Current Page", default=1, type=int, required=False)
pagination_arguments_customer.add_argument("rows_per_page", help="Rows per Page", default=10, type=int, required=False)
pagination_arguments_customer.add_argument("order_by", help="Order By", default="", type=str, required=False)
pagination_arguments_customer.add_argument("sort_by", help="Sort By", default="ASC", type=str, required=False)
pagination_arguments_customer.add_argument("filter_by", help="Filter By", default="", type=str, required=False)

pagination_customer_sellers = reqparse.RequestParser()
pagination_customer_sellers.add_argument("current_page", help="Current Page", default=1, type=int, required=False)
pagination_customer_sellers.add_argument("rows_per_page", help="Rows per Page", default=10, type=int, required=False)
pagination_customer_sellers.add_argument("order_by", help="Order By", default="", type=str, required=False)
pagination_customer_sellers.add_argument("sort_by", help="Sort By", default="ASC", type=str, required=False)
pagination_customer_sellers.add_argument("filter_by", help="Filter By", default="", type=str, required=False)
pagination_customer_sellers.add_argument("has_report", help="Has Report", default=True, type=bool, required=True)
pagination_customer_sellers.add_argument("name_report", help="Name report", default="", type=str, required=False)


report_argumnets_customer = reqparse.RequestParser()
report_argumnets_customer.add_argument("file", type=str, required=True, help="Export", default="csv")
report_ns = Namespace("reportfinance", description="Manage Report Finance")

payload_parser = reqparse.RequestParser()
payload_parser.add_argument('name', type=str, required=True, help='Name', location='form')
payload_parser.add_argument('file', type=FileStorage, required=True, help='With upload .xlsx', location='files')

# payloads processing payments
report_ns_payload = report_ns.model(
    "ProcessingPayments", 
    {   
        "user_id": fields.List(fields.Integer, required=True, example=[1047]), 
        "decision_maker": fields.Boolean(required=True, example=False),
        "flag_id": fields.Integer(required=True, example=87)
    }
)

processing_ns_payload = report_ns.model("ProcessingFlagsPayaments", {"flags_id": fields.Integer(required=True, example=1), "rate": fields.Float(required=True, example=3.6)})

payload_add_flags = report_ns.model("AddFlag", {"name": fields.String(required=True, example="Flag Black"), "rate": fields.Float(required=True, example=3.6)})

payload_delete_payments = report_ns.model("DeletePayments", {"ids": fields.List(fields.Integer, required=True, example=[2, 3, 4, 5, 6])})


payload_delete_ids = report_ns.model(
    "DeleteFlagsIds",
    {
        "ids": fields.List(fields.Integer, required=True, example=[2]),
    },
)

payload_add_decision_maker = report_ns.model(
    "Add_decision_maker",
    {
        "proposal_ids": fields.List(fields.Integer, required=True, example=[2, 3, 4]),
    },
)


@report_ns.route("/import-reports")
class TablesFinanceImportResource(Resource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.payload_parser = reqparse.RequestParser()
        self.payload_parser.add_argument('name', type=str, required=True, help='Name', location='form')
        self.payload_parser.add_argument('file', type=FileStorage, required=True, help='With upload .xlsx or .csv', location='files')

    # @jwt_required()
    @report_ns.doc(description="Import report banker")
    @report_ns.expect(payload_parser, validate=True)
    @cross_origin()
    def post(self):
        """Import report banker"""
        try:
            args = self.payload_parser.parse_args()
            name_report = args['name']
            file = args['file']
            user_id = request.headers.get("Id", request.environ.get("Id"))

            return ReportCore(user_id=user_id).add_report(data={'name': name_report}, file=file)
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong")


@report_ns.route("")
class ReportManage(Resource):

    # @jwt_required()
    @report_ns.doc(description="List payments processing")
    @report_ns.expect(pagination_arguments_customer, validate=True)
    @cross_origin()
    def get(self):
        """List payments processing"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return ReportCore(user_id=user_id).list_processing_payments(data=request.args.to_dict())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))

    # @jwt_required()
    @report_ns.doc(description="Add process payments")
    @report_ns.expect(report_ns_payload, validate=True)
    @cross_origin()
    def post(self):
        """Add process payments with id flag and ids users or unique id"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return ReportCore(user_id=user_id).processing_payments(data=request.get_json())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))


@report_ns.route("/delete-payments")
class DeleteProcessingPayments(Resource):

    # @jwt_required()
    @report_ns.doc(description="Delete process payments")
    @report_ns.expect(payload_delete_payments, validate=True)
    @cross_origin()
    def delete(self):
        """Delete process payments"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return ReportCore(user_id=user_id).delete_processing_payment(data=request.get_json())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))


@report_ns.route("/export-report")
class ExportReportResource(Resource):

    # @jwt_required()
    @report_ns.doc(description="Export processing payment")
    @report_ns.expect(report_argumnets_customer, validate=True)
    @cross_origin()
    def get(self):
        """Export processing payments"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            file_type = request.args.get("file")

            return ReportCore(user_id=user_id).export_processing_payments(file_type=file_type)
        except Exception as e:
            return Response().response(status_code=400, message_id="something_went_wrong", error=True, exception=str(e), traceback=traceback.format_exc(e))

@report_ns.route("/list-import")
class ListImportResource(Resource):

    # @jwt_required()
    @report_ns.doc(description="List report import of platform")
    @report_ns.expect(pagination_arguments_customer, validate=True)
    @cross_origin()
    def get(self):
        """List report import of platform"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))

            return ReportCore(user_id=user_id).list_import(data=request.args.to_dict())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))


@report_ns.route("/delete-imports/<string:name>")
class DeleteResource(Resource):
    # @jwt_required()
    @report_ns.doc(description="Delete imports of platform")
    @cross_origin()
    def delete(self, name: str):
        """Delete imports reports of platform"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))

            return ReportCore(user_id=user_id).delete_imports(name=name)
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))


@report_ns.route("/flags")
class FlagsListResource(Resource):

    # @jwt_required()
    @report_ns.doc(description="list of flags")
    @report_ns.expect(pagination_arguments_customer, validate=True)
    @cross_origin()
    def get(self):
        """List of flags"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))

            return ReportCore(user_id=user_id).list_flags(data=request.args.to_dict())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))

    # @jwt_required()
    @report_ns.doc(description="Add flags")
    @report_ns.expect(payload_add_flags, validate=True)
    @cross_origin()
    def post(self):
        """Add flags"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return ReportCore(user_id=user_id).add_flags(data=request.get_json())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))


@report_ns.route("/flags-delete")
class FlagsDeleteResource(Resource):

    # @jwt_required()
    @report_ns.doc(description="delete flags")
    @report_ns.expect(payload_delete_ids, validate=True)
    @cross_origin()
    def delete(self):
        """Delete flags of platform"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return ReportCore(user_id=user_id).delete_flag(data=request.get_json())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))


@report_ns.route("/sellers")
class ListSellersResource(Resource):

    # @jwt_required()
    @report_ns.doc(description="list of sellers that contain a paid proposal, parameter has report and contains a paid proposal but is not in the report")
    @report_ns.expect(pagination_customer_sellers, validate=True)
    @cross_origin()
    def get(self):
        """list of sellers that contain a paid proposal, parameter has report and contains a paid proposal but is not in the report"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))

            return ReportCore(user_id=user_id).list_sellers(data=request.args.to_dict())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))