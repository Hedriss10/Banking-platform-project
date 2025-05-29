import traceback

from flask import request
from flask_cors import cross_origin
from flask_restx import Namespace, Resource, fields, reqparse
from werkzeug.datastructures import FileStorage

from src.core.proposal import ProposalCore
from src.service.response import Response

# pagination arguments customer
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
    "sort_by", help="Sort By", default="", type=str, required=False
)
pagination_arguments_customer.add_argument(
    "filter_by", help="Filter By", default="", type=str, required=False
)


proposal_ns = Namespace("proposal", description="Manage Proposals")

paylaod_proposal_add = proposal_ns.model(
    "AddProposal",
    {
        "nome": fields.String(required=False, example="name"),
        "data_nascimento": fields.String(required=False, example="10/10/1998"),
        "genero": fields.String(required=False, example="M"),
        "email": fields.String(required=False, example="email@example.com"),
        "cpf": fields.String(required=False, example="123.456.789-00"),
        "naturalidade": fields.String(required=False, example="naturalidade"),
        "cidade_naturalidade": fields.String(
            required=False, example="state_city"
        ),
        "uf_naturalidade": fields.String(required=False, example="DF"),
        "cep": fields.String(require=False, example="40028922"),
        "orgao_emissor": fields.String(required=False, example="SSP"),
        "rg_documento": fields.String(required=False, example="DF"),
        "nome_mae": fields.String(required=False, example="John Senior"),
        "cep": fields.String(required=False, example="40028922"),
        "data_emissao": fields.String(required=False, example="10/10/2016"),
        "uf_cidade": fields.String(required=False, example="UF"),
        "nome_pai": fields.String(required=False, example="Mary Doe"),
        "bairro": fields.String(required=False, example="Centro"),
        "endereco": fields.String(required=False, example="Rua Exemplo"),
        "numero_endereco": fields.String(required=False, example="123"),
        "complemento_endereco": fields.String(
            required=False, example="Apto 45"
        ),
        "cidade": fields.String(required=False, example="Brasília"),
        "valor_salario": fields.Float(required=False, example=5000.00),
        "salario_liquido": fields.Float(required=False, example=4500.00),
        "telefone": fields.String(required=False, example="(61) 99999-9999"),
        "telefone_residencial": fields.String(
            required=False, example="(61) 3333-3333"
        ),
        "telefone_comercial": fields.String(
            required=False, example="(61) 4444-4444"
        ),
        "observe": fields.String(required=False, example="Sem observações"),
        "agencia_banco": fields.String(required=False, example="76"),
        "pix_chave": fields.String(required=False, example="40028922"),
        "agencia": fields.String(required=False, example="0001"),
        "agencia_dv": fields.String(required=False, example="77"),
        "agencia_op": fields.String(required=False, example="341-7"),
        "agency_dvop": fields.String(required=False, example="3"),
        "tipo_conta": fields.String(required=False, example="Corrente"),
        "senha_servidor": fields.String(required=False, example="4137"),
        "matricula": fields.String(required=False, example="registration"),
        "data_dispacho": fields.String(required=False, example="2024-01-15"),
        "margem": fields.Float(required=False, example=12.12),
        "prazo_inicio": fields.Integer(required=False, example=75),
        "prazo_fim": fields.Integer(required=False, example=75),
        "valor_operacao": fields.Float(required=False, example=20517.07),
        "tables_finance_id": fields.Integer(required=False, example=54),
        "financial_agreements_id": fields.Integer(required=False, example=1),
        "loan_operation_id": fields.Integer(required=False, example=2),
        "benefit_id": fields.Integer(required=False, example=1),
    },
)


payload_parser = reqparse.RequestParser()
payload_parser.add_argument(
    "extrato_consignacoes",
    type=FileStorage,
    required=False,
    help="Upload an image (PNG or JPEG)",
    location="files",
)
payload_parser.add_argument(
    "contracheque",
    type=FileStorage,
    required=False,
    help="Upload an image (PNG or JPEG)",
    location="files",
)
payload_parser.add_argument(
    "rg_cnh_completo",
    type=FileStorage,
    required=False,
    help="Upload an image (PNG or JPEG)",
    location="files",
)
payload_parser.add_argument(
    "rg_verso",
    type=FileStorage,
    required=False,
    help="Upload an image (PNG or JPEG)",
    location="files",
)
payload_parser.add_argument(
    "rg_frente",
    type=FileStorage,
    required=False,
    help="Upload an image (PNG or JPEG)",
    location="files",
)
payload_parser.add_argument(
    "comprovante_residencia",
    type=FileStorage,
    required=False,
    help="Upload an image (PNG or JPEG)",
    location="files",
)
payload_parser.add_argument(
    "selfie",
    type=FileStorage,
    required=False,
    help="Upload an image (PNG or JPEG)",
    location="files",
)
payload_parser.add_argument(
    "detalhamento_inss",
    type=FileStorage,
    required=False,
    help="Upload an image (PNG or JPEG)",
    location="files",
)


payload_parser_edit = reqparse.RequestParser()
payload_parser_edit.add_argument("nome", type=str, required=False, help="Goku")


@proposal_ns.route("")
class ListProposalResource(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.payload_parser = reqparse.RequestParser()
        self.payload_parser.add_argument(
            "extrato_consignacoes",
            type=FileStorage,
            required=False,
            help="Upload an image (PNG or JPEG)",
            location="files",
        )

    # @jwt_required()
    @proposal_ns.doc(description="Add Proposal")
    @proposal_ns.expect(payload_parser)
    @cross_origin()
    def post(self):
        """Add proposal with filter json dynammic"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            if not user_id:
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="missing_user_id",
                    exception="User ID is required but not provided in the request headers.",
                )

            return ProposalCore(user_id=user_id).add_proposal(
                data=request.form, image_data=request.files
            )
        except Exception as e:
            return Response().response(
                status_code=500,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(),
            )

    # # @jwt_required()
    @proposal_ns.doc(description="List proposal")
    @proposal_ns.expect(pagination_arguments_customer, validate=True)
    @cross_origin()
    def get(self):
        """List proposal order by created_at"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            if not user_id:
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="missing_user_id",
                    exception="User ID is required but not provided in the request headers.",
                )

            return ProposalCore(user_id=user_id).list_proposal(
                data=request.args.to_dict()
            )
        except Exception as e:
            return Response().response(
                status_code=500,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(),
            )


@proposal_ns.route("/<int:id>")
class ProposalResource(Resource):
    # @jwt_required()
    @proposal_ns.doc(description="Get Proposal with Id")
    @cross_origin()
    def get(self, id):
        """Get proposal with Id"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            if not user_id:
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="missing_user_id",
                    exception="User ID is required but not provided in the request headers.",
                )

            return ProposalCore(user_id=user_id).get_proposal(id=id)
        except Exception as e:
            return Response().response(
                status_code=500,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(),
            )

    # @jwt_required()
    @proposal_ns.doc(description="Edit with json dynamic")
    @proposal_ns.expect(paylaod_proposal_add)
    @cross_origin()
    def put(self, id):
        """Edit with json dynamic"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            if not user_id:
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="missing_user_id",
                    exception="User ID is required but not provided in the request headers.",
                )

            return ProposalCore(user_id=user_id).update_proposal(
                proposal_id=id, data=request.form, image=request.files
            )
        except Exception as e:
            return Response().response(
                status_code=500,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(),
            )

    # @jwt_required()
    @proposal_ns.doc(description="Delete proposal")
    @cross_origin()
    def delete(self, id):
        """Delete proposal"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            if not user_id:
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="missing_user_id",
                    exception="User ID is required but not provided in the request headers.",
                )

            return ProposalCore(user_id=user_id).delete_proposal(id=id)
        except Exception as e:
            return Response().response(
                status_code=500,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(),
            )
