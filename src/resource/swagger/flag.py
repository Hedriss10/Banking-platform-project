from flask_restx import fields, reqparse

class FlagsFactoryPayloads:
    @staticmethod
    def payload_add_flags(api):
        return api.model(
            "AddFlags",
            {
                "name": fields.String(required=True, example="Flag Black"),
                "rate": fields.Float(required=True, example=3.6)
            }
        )
        
    @staticmethod
    def payload_delete_flags(api):
        return api.model(
            "DeleteFlags",
            {
                "ids": fields.List(fields.Integer, required=True, example=[2, 3, 4, 5, 6])
            }
        )
        
    @staticmethod    
    def pagination_arguments_parser():
        paginantion_arguments_flags = reqparse.RequestParser()
        paginantion_arguments_flags.add_argument("current_page", help="Current Page", default=1, type=int, required=False)
        paginantion_arguments_flags.add_argument("rows_per_page", help="Rows per Page", default=10, type=int, required=False)
        paginantion_arguments_flags.add_argument("order_by", help="Order By", default="", type=str, required=False)
        paginantion_arguments_flags.add_argument("sort_by", help="Sort By", default="ASC", type=str, required=False)
        paginantion_arguments_flags.add_argument("filter_value", help="Filter By", default="", type=str, required=False)
        return paginantion_arguments_flags