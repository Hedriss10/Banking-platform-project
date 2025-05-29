from flask_restx import fields, reqparse


class FactoryPayloadsBankers:
    @staticmethod
    def add_payload_banker(api):
        return api.model(
            "BankersAddNewBankers",
            {
                "name": fields.String(required=True, example="Banco"),
            },
        )

    @staticmethod
    def edit_payload_banker(api):
        return api.model(
            "BankersPut",
            {
                "name": fields.String(required=True, example="Banco"),
            },
        )

    @staticmethod
    def pagination_arguments_parser():
        parser = reqparse.RequestParser()
        parser.add_argument(
            "current_page",
            help="Current Page",
            default=1,
            type=int,
            required=False,
        )
        parser.add_argument(
            "rows_per_page",
            help="Rows per Page",
            default=10,
            type=int,
            required=False,
        )
        parser.add_argument(
            "order_by", help="Order By", default="", type=str, required=False
        )
        parser.add_argument(
            "sort_by", help="Sort By", default="", type=str, required=False
        )
        parser.add_argument(
            "filter_by", help="Filter By", default="", type=str, required=False
        )
        parser.add_argument(
            "filter_value",
            help="Filter Value",
            default="",
            type=str,
            required=False,
        )
        return parser


class FactoryPayloadsFinancialAgreements:
    @staticmethod
    def paylaod_add_financialagreements(api):
        return api.model(
            "AddFinancialAgreemeents",
            {
                "name": fields.String(required=True, example="Novo Orgão"),
                "banker_id": fields.Integer(required=True, example=2),
            },
        )

    @staticmethod
    def paylaod_edit_financialagreements(api):
        return api.model(
            "EditFinancialAgreemeents",
            {"name": fields.String(required=True, example="Novo Orgão")},
        )

    @staticmethod
    def pagination_arguments_parser():
        parser = reqparse.RequestParser()
        parser.add_argument(
            "current_page",
            help="Current Page",
            default=1,
            type=int,
            required=False,
        )
        parser.add_argument(
            "rows_per_page",
            help="Rows per Page",
            default=10,
            type=int,
            required=False,
        )
        parser.add_argument(
            "order_by", help="Order By", default="", type=str, required=False
        )
        parser.add_argument(
            "sort_by", help="Sort By", default="", type=str, required=False
        )
        parser.add_argument(
            "filter_by", help="Filter By", default="", type=str, required=False
        )
        parser.add_argument(
            "filter_value",
            help="Filter Value",
            default="",
            type=str,
            required=False,
        )
        return parser


class FactoryPayloadsTablesFinance:
    @staticmethod
    def pagination_arguments_parser():
        parser = reqparse.RequestParser()
        parser.add_argument(
            "current_page",
            help="Current Page",
            default=1,
            type=int,
            required=False,
        )
        parser.add_argument(
            "rows_per_page",
            help="Rows per Page",
            default=10,
            type=int,
            required=False,
        )
        parser.add_argument(
            "order_by", help="Order By", default="", type=str, required=False
        )
        parser.add_argument(
            "sort_by", help="Sort By", default="", type=str, required=False
        )
        parser.add_argument(
            "filter_by", help="Filter By", default="", type=str, required=False
        )
        parser.add_argument(
            "filter_value",
            help="Filter Value",
            default="",
            type=str,
            required=False,
        )
        return parser

    @staticmethod
    def add_payload_tablesfinance(api):
        return api.model(
            "AddTablesFinance",
            {
                "financial_agreements_id": fields.Integer(
                    required=True, example=1
                ),
                "name": fields.String(required=True, example="INSS Flex 6"),
                "table_code": fields.String(required=True, example="40028922"),
                "type_table": fields.String(
                    required=True, example="Margem Livre"
                ),
                "start_term": fields.String(required=True, example="76"),
                "end_term": fields.String(required=True, example="76"),
                "start_rate": fields.String(required=True, example="2.4"),
                "end_rate": fields.String(required=True, example="3.0"),
                "rate": fields.Float(required=True, example=3.6),
                "issue_date": fields.DateTime(
                    required=True, example="2025-01-10"
                ),
            },
        )

    @staticmethod
    def payload_delete_tables_finance(api):
        return api.model(
            "DeleteTablesIds",
            {
                "ids": fields.List(
                    fields.Integer, required=True, example=[1, 2, 3, 4, 5, 6]
                ),
            },
        )
