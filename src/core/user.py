# src/core/users.py
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from src.db.database import db
from src.models.user import User
from src.service.response import Response
from src.utils.log import logdb
from src.utils.pagination import Pagination


class UsersCore:
    def __init__(self, user_id: int, *args, **kwargs) -> None:
        self.user_id = user_id
        self.User = User

    def list_users(self, data: dict):
        current_page = int(data.get("current_page", 1))
        rows_per_page = int(data.get("rows_per_page", 10))

        if current_page < 1:
            current_page = 1
        if rows_per_page < 1:
            rows_per_page = 1

        pagination = Pagination().pagination(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=data.get("sort_by", ""),
            order_by=data.get("order_by", ""),
            filter_by=data.get("filter_value", ""),
            filter_value=data.get("filter_value", "")
        )
        
        query = self.User.query.filter(self.User.is_deleted == False, self.User.is_block == False)

        # Filtro dinâmico com ILIKE e unaccent
        if pagination["filter_value"]:
            filter_value = f"%{pagination['filter_value']}%"
            query = query.filter(
                db.or_(
                    func.unaccent(self.User.username).ilike(func.unaccent(filter_value)),
                    func.unaccent(self.User.cpf).ilike(func.unaccent(filter_value))
                )
            )

        # Ordenação dinâmica
        if pagination["order_by"] and pagination["sort_by"]:
            sort_column = getattr(self.User, pagination["order_by"], None)
            if sort_column:
                query = query.order_by(
                    sort_column.asc() if pagination["sort_by"] == "asc" else sort_column.desc()
                )
        else:
            query = query.order_by(self.User.id.desc())  # Ordem padrão por id DESC

        # Paginação
        total = query.count()
        users = query.offset(pagination["offset"]).limit(pagination["limit"]).all()

        if not users:
            return Response().response(
                status_code=404,
                error=True,
                message_id="users_list_not_found",
                exception="Not found",
                data=[]
            )

        # Serializar os dados
        user = [
            {
                "id": user.id,
                "cpf": user.cpf,
                "username": user.username,
                "lastname": user.lastname,
                "email": user.email,
                "role": user.role,
                "typecontract": user.typecontract,
                "is_deleted": user.is_deleted,
                "is_block": user.is_block,
                "create_at": user.create_at.strftime("%Y-%m-%d")
            }
            for user in users
        ]

        metadata = Pagination().metadata(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=pagination["sort_by"],
            order_by=pagination["order_by"],
            filter_by=pagination["filter_by"],
            total=total
        )
        return Response().response(
            status_code=200,
            message_id="users_list_users_successful",
            data=user,
            metadata=metadata
        )

    def get_user(self, id):
        user = self.User.query.filter_by(id=id).first()

        if not user:
            return Response().response(
                status_code=404,
                error=True,
                message_id="user_get_not_found",
                exception="Not found",
                data=None
            )

        user_data = user.__dict__
        user_data.pop('_sa_instance_state', None)
        return Response().response(
            status_code=200,
            message_id="user_get_successful",
            data=user_data
        )

    def add_user(self, data: dict):
        try:
            if not data.get("cpf"):
                return Response().response(
                    status_code=400,
                    message_id="cpf_is_required",
                    exception="CPF is required"
                )

            password = data.get("password")
            hashed_password = generate_password_hash(password, method="scrypt") if password else None

            new_user = self.User(
                cpf=data.get("cpf"),
                username=data.get("username"),
                lastname=data.get("lastname"),
                email=data.get("email"),
                password=hashed_password,
                typecontract=data.get("typecontract"),
                is_first_acess=True
            )
            self.User.query.session.add(new_user)
            self.User.query.session.commit()

            user_data = new_user.__dict__
            user_data.pop('_sa_instance_state', None)
            return Response().response(
                status_code=200,
                message_id="user_add_successful",
                metadata={"dict": data},
                data=user_data
            )

        except IntegrityError as e:
            self.User.query.session.rollback()
            logdb("warning", "CPF with this cpf already exists")
            return Response().response(
                status_code=400,
                message_id="cpf_with_email_already_exists",
                error=True,
                exception="CPF with this cpf already exists"
            )

    def update_user(self, id: int, data: dict):
        try:
            if not id or not data:
                return Response().response(
                    status_code=400,
                    message_id="id_or_data_is_required",
                    exception="ID or Data is required"
                )

            user = self.User.query.filter_by(id=id).first()
            if not user:
                return Response().response(
                    status_code=404,
                    message_id="user_get_not_found",
                    exception="Not found"
                )

            for key, value in data.items():
                if key == "password" and value:
                    value = generate_password_hash(value, method="scrypt")
                if hasattr(user, key):
                    setattr(user, key, value)

            self.User.query.session.commit()
            return Response().response(
                status_code=200,
                message_id="user_edit_successful"
            )

        except IntegrityError:
            self.User.query.session.rollback()
            logdb("warning", "CPF with this cpf already exists")
            return Response().response(
                status_code=400,
                message_id="cpf_with_email_already_exists",
                error=True,
                exception="CPF with this cpf already exists"
            )
        except Exception as e:
            self.User.query.session.rollback()
            logdb("error", message=f"Error edit user {e}")
            return Response().response(
                status_code=400,
                message_id="error_edit_user",
                error=True,
                exception="bad request"
            )

    def delete_user(self, id):
        user = self.User.query.filter_by(id=id).first()
        if not user:
            return Response().response(
                status_code=404,
                error=True,
                message_id="user_get_not_found",
                exception="Not found",
                data=None
            )
        # soft delete
        user.is_deleted = True
        self.User.query.session.commit()

        user_data = user.__dict__
        user_data.pop('_sa_instance_state', None)
        return Response().response(
            status_code=200,
            message_id="user_delete_successful",
            data=user_data
        )