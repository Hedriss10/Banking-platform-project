import traceback

from src.core.statistics import StatisticsCore
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


profit_ns = Namespace("profit", description="Profit Proposals of Sellers Manager")


@profit_ns.route("")
class ListProfitResource(Resource):
    
    # @jwt_required()
    @profit_ns.doc(description="Get List All Profit")
    @profit_ns.expect(pagination_arguments_customer, validate=True)
    @cross_origin()
    def get(self):
        """Get List All Profit"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return StatisticsCore(user_id=user_id).list_hold_profit_sellers(data=request.args.to_dict())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc())