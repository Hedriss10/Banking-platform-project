from flask_restx import fields, reqparse


class PayloadFactoryHourspoint:
   
    @staticmethod
    def add_time_point(api):
        return api.model(
            "AddTimePoint",
            {
                "employee_id": fields.Integer(required=True, example=15),
                "data": fields.DateTime(required=True, example="2024-12-12T09:00:00"),
                "entrada": fields.DateTime(required=True, example="2024-12-12T08:00:00"),
                "saida": fields.DateTime(required=True, example="2024-12-12T18:00:00"),
                "entrada_almoco": fields.DateTime(required=True, example="2024-12-12T12:00:00"),
                "saida_almoco": fields.DateTime(required=True, example="2024-12-12T13:00:00"),
                "entrada_lanche": fields.DateTime(required=True, example="2024-12-12T15:00:00"),
                "saida_lanche": fields.DateTime(required=True, example="2024-12-12T15:15:00"),
            }
        )
   
    @staticmethod
    def add_justification_for_delay(api):
        return api.model(
            "AddJustificationForDelay",
            {
                "employee_id": fields.Integer(required=True, example=15),
                "data": fields.DateTime(required=True, example="2024-12-12T09:00:00"),
                "justificativa": fields.String(required=True, example="Funcinario Thon chegou atrasado, verificar com o Master!")
            }
        )
   
    @staticmethod
    def add_holiday(api):
        return api.model(
            "AddHoliday",
            {
                "employee_id": fields.Integer(required=True, example=15),
                "data": fields.DateTime(required=True, example="2024-12-12T09:00:00"),
                "estado": fields.String(required=True, example="DF"),
                "tipo": fields.String(required=True, example="Feriado"),
                "descricao": fields.String(required=True, example="Feriado Estadual")
            }
        )
   
    @staticmethod
    def add_absence(api):
        return api.model(
            "AddAbsence",
            {
                "employee_id": fields.Integer(required=True, example=15),
                "data": fields.DateTime(required=True, example="2024-12-12T09:00:00"),
                "descricao": fields.String(required=True, example="Não respondeu o whatsapp."),
                "justificativa": fields.String(required=True, example="Não apresentou nenhuma justificativa."),
                "justificavel": fields.Boolean(required=True, example=False),
            }
        )
    
    @staticmethod
    def edit_absence(api):
        return api.model(
            "EditAbasence",
            {
                "descricao": fields.String(required=True, example="Sim ele respondeu o whatsapp, vai está presente mas chegará atrasado."),
                "justificavel": fields.Boolean(required=True, example=False),
            }
        )
    
    @staticmethod
    def add_vacation(api):
        return api.model(
            "AddVocation",
            {
                "employee_id": fields.Integer(required=True, example=15),
                "data_inicio": fields.DateTime(required=True, example="2024-12-12T09:00:00"),
                "data_fim": fields.DateTime(required=True, example="2024-12-12T08:00:00"),
                "aprovado": fields.Boolean(required=True, example=True)
            }
        )
        
    @staticmethod
    def edit_vacation(api):
        return api.model(
            "EditVacation",
            {
                "data_inicio": fields.DateTime(required=True, example="2024-12-12T09:00:00"),
                "data_fim": fields.DateTime(required=True, example="2024-12-12T08:00:00"),
                "aprovado": fields.Boolean(required=True, example=True)
            }
        )

    @staticmethod
    def pagination_payload(api):
        return api.model(
            "PaginationArgumentsCustomer",
            {
                "page": fields.Integer(required=False, example=15),
                "limit": fields.Integer(required=False, example=10),
            },
        )

    @staticmethod
    def pagination_arguments_parser():
        parser = reqparse.RequestParser()
        parser.add_argument("current_page", help="Current Page", default=1, type=int, required=False)
        parser.add_argument("rows_per_page", help="Rows per Page", default=10, type=int, required=False)
        parser.add_argument("order_by", help="Order By", default="", type=str, required=False)
        parser.add_argument("sort_by", help="Sort By", default="", type=str, required=False)
        parser.add_argument("filter_by", help="Filter By", default="", type=str, required=False)
        parser.add_argument("filter_value", help="Filter Value", default="", type=str, required=False)
        return parser


class PaylaodFactoryRooms:
    
    @staticmethod
    def add_payload_room(api):
        return api.model(
            "AddRooms",
            {
                "name": fields.String(required=True, example="Sala Guerra"),
            },
        )
    
    @staticmethod
    def edit_payload_room(api):
        return api.model(
            "EditRooms",
            {
                "name": fields.String(required=True, example="Sala Guerra"),
            },
        )
    
    @staticmethod
    def add_asscoaite_user_rooms(api):
        return api.model(
            "AssociateRoomsUsers",
            {
                "ids": fields.List(fields.Integer, required=True, example=[1, 2, 3, 4, 5, 6]),
                "rooms_id": fields.List(fields.Integer, required=True, example=[1])
            }
        )
    
    @staticmethod
    def delete_associate_rooms(api):
        return api.model(
            "DeleteAssociateRooms",
            {
                "ids": fields.List(fields.Integer, required=True, example=[1, 2, 3, 4, 5, 6])
            }
        )

    @staticmethod
    def pagination_arguments_parser():
        parser = reqparse.RequestParser()
        parser.add_argument("current_page", help="Current Page", default=1, type=int, required=False)
        parser.add_argument("rows_per_page", help="Rows per Page", default=10, type=int, required=False)
        parser.add_argument("order_by", help="Order By", default="", type=str, required=False)
        parser.add_argument("sort_by", help="Sort By", default="", type=str, required=False)
        parser.add_argument("filter_by", help="Filter By", default="", type=str, required=False)
        parser.add_argument("filter_value", help="Filter Value", default="", type=str, required=False)
        return parser
    
    
class PayloadFactoryRole:
    
    @staticmethod
    def add_payload_role(api):
        return api.model(
            "AddRole",
            {
                "name": fields.String(required=True, example="Suporte")
            }
        )
    
    
    @staticmethod
    def pagination_arguments_parser():
        parser = reqparse.RequestParser()
        parser.add_argument("current_page", help="Current Page", default=1, type=int, required=False)
        parser.add_argument("rows_per_page", help="Rows per Page", default=10, type=int, required=False)
        parser.add_argument("order_by", help="Order By", default="", type=str, required=False)
        parser.add_argument("sort_by", help="Sort By", default="", type=str, required=False)
        parser.add_argument("filter_by", help="Filter By", default="", type=str, required=False)
        parser.add_argument("filter_value", help="Filter Value", default="", type=str, required=False)
        return parser