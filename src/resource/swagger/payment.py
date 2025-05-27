from flask_restx import fields, reqparse


class PaymentsFactoryPayloads:
    
    @staticmethod
    def payload_add_payments(api):
        return api.model(
            "ProcessingPayment",
            {
                "flag_id": fields.Integer(required=False, example=1),
                "proposal_id": fields.List(fields.Integer, required=True, example=[1, 2, 3]),
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
        pagination.add_argument("sort_by", help="Sort By", default="", type=str, required=False)
        pagination.add_argument("order_by", help="Order By", default="asc", type=str, required=False)
        pagination.add_argument("filter_by", help="Filter By", default="", type=str, required=False)
        pagination.add_argument("filter_value", help="Filter Value", default="", type=str, required=False)
        return pagination
    
    @staticmethod
    def payload_add_service_provided(api):
        return api.model(
            "ProcessingPayment",
            {
                "proposal_id": fields.List(fields.Integer, required=True, example=[1, 2, 3]),
                "user_id": fields.List(fields.Integer, required=True, example=[1]),
                "valor_operacao": fields.List(fields.Float, required=False, example=[100.00, 200.00])
            }
        )
    
    @staticmethod
    def payload_delete_service_provided(api):
        return api.model(
            "DeletePayments",
            {
                "proposal_id": fields.List(fields.Integer, required=True, example=[2, 3, 4, 5, 6])
            }
        )