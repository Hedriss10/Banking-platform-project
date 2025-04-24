import traceback

from flask import request
from flask_cors import cross_origin
from flask_restx import Namespace, Resource, reqparse

from src.core.dashboard import DashboardCore
from src.service.response import Response

pagination_arguments_customer = reqparse.RequestParser()
pagination_arguments_customer.add_argument("current_page", help="Current Page", default=1, type=int, required=False)
pagination_arguments_customer.add_argument("rows_per_page", help="Rows per Page", default=10, type=int, required=False)
pagination_arguments_customer.add_argument("order_by", help="Order By", default="", type=str, required=False)
pagination_arguments_customer.add_argument("sort_by", help="Sort By", default="", type=str, required=False)
pagination_arguments_customer.add_argument("filter_by", help="Filter By", default="", type=str, required=False)


dashboard_ns = Namespace("dashboard", description="Dashboard Manager")


@dashboard_ns.route("/sales-paid")
class DashBoardSalesPaid(Resource):

    # @jwt_required()
    @dashboard_ns.doc(description="Get Sales Paid")
    @cross_origin()
    def get(self):
        """Get Sales Paid"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))      
            
            return DashboardCore(user_id=user_id).sales_paid()
        except Exception as e:
            return Response().response(status_code=500, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc())

@dashboard_ns.route("/status-proposals")
class DashBoardStatusProposals(Resource):
    # @jwt_required()
    @dashboard_ns.doc(description="Get Status Proposals")
    @cross_origin()   
    def get(self):
        """Get Status Proposals"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))      
            
            return DashboardCore(user_id=user_id).status_proposals()
        except Exception as e:
            return Response().response(status_code=500, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc())

@dashboard_ns.route("/sales-paid-ranking")
class DashBoardSallesPaidRanking(Resource):
    # @jwt_required()
    @dashboard_ns.doc(description="Salles Sales Paid Ranking")
    @dashboard_ns.expect(pagination_arguments_customer, validate=True)
    @cross_origin() 
    def get(self):
        """Salles Sales Paid Ranking"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))      
            
            return DashboardCore(user_id=user_id).salles_sales_paid_ranking(data=request.args.to_dict())
        except Exception as e:
            print(e)
            return Response().response(status_code=500, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc())