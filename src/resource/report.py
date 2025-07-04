import traceback

from flask import request
from flask_cors import cross_origin
from flask_restx import Namespace, Resource, reqparse
from werkzeug.datastructures import FileStorage

from src.core.finance import ReportCore
from src.service.response import Response

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
    "sort_by", help="Sort By", default="ASC", type=str, required=False
)
pagination_arguments_customer.add_argument(
    "filter_by", help="Filter By", default="", type=str, required=False
)


report_argumnets_customer = reqparse.RequestParser()
report_argumnets_customer.add_argument(
    "file", type=str, required=True, help="Export", default="csv"
)
report_ns = Namespace("report", description="Manage Report Finance")

payload_parser = reqparse.RequestParser()
payload_parser.add_argument(
    "name", type=str, required=True, help="Name", location="form"
)
payload_parser.add_argument(
    "file",
    type=FileStorage,
    required=True,
    help="With upload .xlsx",
    location="files",
)


@report_ns.route("/import-reports")
class TablesFinanceImportResource(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.payload_parser = reqparse.RequestParser()
        self.payload_parser.add_argument(
            "name", type=str, required=True, help="Name", location="form"
        )
        self.payload_parser.add_argument(
            "file",
            type=FileStorage,
            required=True,
            help="With upload .xlsx or .csv",
            location="files",
        )

    # @jwt_required()
    @report_ns.doc(description="Import report of banker")
    @report_ns.expect(payload_parser, validate=True)
    @cross_origin()
    def post(self):
        """Import report of banker"""
        try:
            args = self.payload_parser.parse_args()
            name_report = args["name"]
            file = args["file"]
            user_id = request.headers.get("Id", request.environ.get("Id"))

            return ReportCore(user_id=user_id).add_report(
                data={"name": name_report}, file=file
            )
        except Exception:
            return Response().response(
                status_code=400, error=True, message_id="something_went_wrong"
            )


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

            return ReportCore(user_id=user_id).list_report_imports(
                data=request.args.to_dict()
            )
        except Exception as e:
            return Response().response(
                status_code=400,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(e),
            )


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
            return Response().response(
                status_code=400,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(e),
            )
