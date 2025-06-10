from flask_restx import fields, reqparse


class PaylaodFactoryUser:
    @staticmethod
    def add_user_payload(api):
        return api.model(
            "AddUsser",
            {
                "username": fields.String(
                    required=False, max_length=150, example="David"
                ),
                "lastname": fields.String(
                    required=False, max_length=150, example="Back"
                ),
                "email": fields.String(
                    required=False, max_length=50, example="usersbs@teste.com"
                ),
                "cpf": fields.String(required=True, max_length=25, example=""),
                "password": fields.String(
                    required=False, max_length=250, example="********"
                ),
                "typecontract": fields.String(
                    required=False, max_length=50, example="Funcionario"
                ),
                "role": fields.String(
                    required=False, max_length=50, example="Administrador"
                ),
                "matricula": fields.String(required=True, example="40028922"),
                "numero_pis": fields.String(
                    required=True, example="414786431503"
                ),
                "empresa": fields.String(required=True, example="BSC4"),
                "situacao_cadastro": fields.String(
                    required=True, example="ativo"
                ),
                "carga_horaria_semanal": fields.Integer(
                    required=True, example=44
                ),
            },
        )

    @staticmethod
    def edit_user_payload(api):
        return api.model(
            "EditUser",
            {
                "username": fields.String(
                    required=False, max_length=150, example="David"
                ),
                "lastname": fields.String(
                    required=False, max_length=150, example="Back"
                ),
                "email": fields.String(
                    required=False, max_length=50, example="usersbs@teste.com"
                ),
                "cpf": fields.String(
                    required=False, max_length=25, example=""
                ),
                "password": fields.String(
                    required=False, max_length=250, example="********"
                ),
                "typecontract": fields.String(
                    required=False, max_length=50, example="Funcionario"
                ),
                "role": fields.String(
                    required=False, max_length=50, example="Administrador"
                ),
                "is_admin": fields.Boolean(required=False, example=False),
                "is_block": fields.Boolean(required=False, example=False),
                "is_acctive": fields.Boolean(required=False, example=False),
                "is_first_acess": fields.Boolean(
                    required=False, example=False
                ),
                "matricula": fields.String(required=False, example="40028922"),
                "numero_pis": fields.String(
                    required=False, example="40024-32313-3"
                ),
                "empresa": fields.String(required=False, example="BSC4"),
                "situacao_cadastro": fields.String(
                    required=False, example="ativo"
                ),
                "carga_horaria_semanal": fields.Integer(
                    required=False, example=44
                ),
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
