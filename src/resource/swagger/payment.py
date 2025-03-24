from flask_restx import fields, reqparse


class PaymentsFactoryPayloads:
    
    @staticmethod
    def payload_add_payments(api):
        return api.model(
            "ProcessingPayment",
            {
                "flag_id": fields.Integer(required=False, example=1),
                "decision_maker": fields.Boolean(required=False, example=True),
                "user_id": fields.List(fields.Integer, required=True, example=[1])
            }
        )
        
    @staticmethod
    def payload_delete_payments(api):
        return api.model(
            "DeletePayments",
            {
                "ids": fields.List(fields.Integer, required=True, example=[2, 3, 4, 5, 6])
            }
        )
        
        
    @staticmethod
    def pagination_args_parse():
        pagination_arguments_payment = reqparse.RequestParser()
        pagination_arguments_payment.add_argument("current_page", help="Current Page", default=1, type=int, required=False)
        pagination_arguments_payment.add_argument("rows_per_page", help="Rows per Page", default=10, type=int, required=False)
        pagination_arguments_payment.add_argument("order_by", help="Order By", default="", type=str, required=False)
        pagination_arguments_payment.add_argument("sort_by", help="Sort By", default="ASC", type=str, required=False)
        pagination_arguments_payment.add_argument("filter_by", help="Filter By", default="", type=str, required=False)
        return pagination_arguments_payment
        
    @staticmethod
    def pagination_list_payments_sellers():
        pagination = reqparse.RequestParser()
        pagination.add_argument("current_page", help="Current Page", default=1, type=int, required=False)
        pagination.add_argument("rows_per_page", help="Rows per Page", default=10, type=int, required=False)
        pagination.add_argument("order_by", help="Order By", default="", type=str, required=False)
        pagination.add_argument("sort_by", help="Sort By", default="ASC", type=str, required=False)
        pagination.add_argument("filter_by", help="Filter By", default="", type=str, required=False)
        pagination.add_argument("has_report", help="Has Report", default=True, type=bool, required=True)
        pagination.add_argument("name_report", help="Name report", default="", type=str, required=False)
        return pagination