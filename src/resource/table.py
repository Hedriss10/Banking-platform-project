import traceback

from flask import request
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, reqparse
from werkzeug.datastructures import FileStorage

from src.core.finance import TablesCore
from src.resource.swagger.factorypayloadsFinance import FactoryPayloadsTablesFinance
from src.service.response import Response

tables_ns = Namespace("table", description="Manage Tables Finance Manager")

pagination_arguments_customer = FactoryPayloadsTablesFinance.pagination_arguments_parser()
paylaod_add_tables = FactoryPayloadsTablesFinance.add_payload_tablesfinance(tables_ns)
paylaod_delete_ids = FactoryPayloadsTablesFinance.payload_delete_tables_finance(tables_ns)

# payload parser for import tables
payload_parser = reqparse.RequestParser()
payload_parser.add_argument('financialagreements_id', type=int, required=True, help='Id financialagreements', location='form')
payload_parser.add_argument('issue_date', type=str, required=True, help='Date issue of table', location='form')
payload_parser.add_argument('file', type=FileStorage, required=True, help='With upload .xlsx', location='files')


@tables_ns.route("/import-tables")
class TablesFinanceImportResource(Resource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.payload_parser = reqparse.RequestParser()
        self.payload_parser.add_argument('financialagreements_id', type=int, required=True, help='Id financialagreements', location='form')
        self.payload_parser.add_argument('issue_date', type=str, required=True, help='Date issue of table', location='form')
        self.payload_parser.add_argument('file', type=FileStorage, required=True, help='With upload .xlsx', location='files')

    # @jwt_required()
    @tables_ns.doc(description="Import tables finance")
    @tables_ns.expect(payload_parser, validate=True)
    @cross_origin()
    def post(self):
        """Import tables finance"""
        try:
            args = self.payload_parser.parse_args()
            issue_date = args['issue_date']
            financialagreements_id = args['financialagreements_id']
            file = args['file']
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return TablesCore(user_id=user_id).add_tables_import(data={'financialagreements_id': financialagreements_id, 'issue_date': issue_date}, file=file)
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))


@tables_ns.route("")
class TablesFinanceResource(Resource):

    # @jwt_required()
    @tables_ns.doc(description="Add one tables")
    @tables_ns.expect(paylaod_add_tables, validate=True)
    @cross_origin()
    def post(self):
        """Add one tables"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return TablesCore(user_id=user_id).add_table(data=request.get_json())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))


@tables_ns.route("/<int:id>")
class TablesFinanceResourceById(Resource):
    # @jwt_required()
    @tables_ns.doc(description="List board tables banker_id and financialagreements_id")
    @tables_ns.expect(pagination_arguments_customer, validate=True)
    @cross_origin()
    def get(self, id: int):
        """List tables with board filter by in banker_id with financial_agreements"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return TablesCore(user_id=user_id).list_board_table(data=request.args.to_dict(), financial_agreements_id=id)
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))
        
    @tables_ns.doc(description="Delete all tables with ids")
    @tables_ns.expect(paylaod_delete_ids, validate=True)
    @cross_origin()
    def delete(self, id: int):
        """Delete all tables with ids"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))

            return TablesCore(user_id=user_id).delete_tables_ids(data=request.get_json(), id=id)
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))

@tables_ns.route("/ranks")
class RanksTableFinancial(Resource):

    # @jwt_required()
    @tables_ns.doc(description="List ranks tables")
    @tables_ns.expect(pagination_arguments_customer, validate=True)
    @cross_origin()
    def get(self):
        """List ranks tables"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))

            return TablesCore(user_id=user_id).rank_comission(data=request.args.to_dict())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(exit))
