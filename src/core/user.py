# src/core/users.py
from sqlalchemy import func, insert, or_, outerjoin, select
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from src.db.database import db
from src.models.models import Employee, User
from src.service.response import Response
from src.utils.log import logdb
from src.utils.metadata import Metadata
from src.utils.pagination import Pagination

STATUS_MAP = {
    'ativo': 'ativo',
    'inativo': 'inativo',
    'suspenso': 'suspenso',
    'ATIVO': 'ativo',
    'INATIVO': 'inativo',
    'SUSPENSO': 'suspenso',
    'Ativo': 'ativo',
    'Inativo': 'inativo',
    'Suspenso': 'suspenso'
}

class UsersCore:
    def __init__(self, user_id: int, *args, **kwargs) -> None:
        self.user_id = user_id
        self.user = User
        self.employee = Employee

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
            filter_by=data.get("filter_by", ""),
            filter_value=data.get("filter_value", "")
        )
        
        # query = self.user.query.filter(self.user.is_deleted == False, self.user.is_block == False)
        stmt = select(
            self.user.id,
            self.user.cpf,
            self.user.username,
            self.user.lastname,
            self.user.email,
            self.user.role,
            self.user.typecontract,
            self.user.is_deleted,
            self.user.is_block,
            self.user.create_at
        ).where(self.user.is_deleted == False, self.user.is_block == False)

        # Filtro dinâmico com ILIKE e unaccent
        if pagination["filter_by"]:
            filter_value = f"%{pagination['filter_by']}%"
            stmt = stmt.filter(
                db.or_(
                    func.unaccent(self.user.username).ilike(func.unaccent(filter_value)),
                    func.unaccent(self.user.cpf).ilike(func.unaccent(filter_value))
                )
            )

        # Ordenação dinâmica
        if pagination["order_by"] and pagination["sort_by"]:
            sort_column = getattr(self.user, pagination["order_by"], None)
            if sort_column:
                stmt = stmt.order_by(
                    sort_column.asc() if pagination["sort_by"] == "asc" else sort_column.desc()
                )
        else:
            stmt = stmt.order_by(self.user.id.desc())  # Ordem padrão por id DESC

        # pagination
        paginated_stmt = stmt.offset(pagination["offset"]).limit(pagination["limit"])
        results = db.session.execute(paginated_stmt).fetchall()

        if not results:
            return Response().response(
                status_code=404,
                error=True,
                message_id="users_list_not_found",
                exception="Not found"
            )

        result = db.session.execute(stmt).fetchall()
        
        total = db.session.execute(select(func.count(self.user.id))).scalar()
        
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
            data=Metadata(result).model_to_list(),
            metadata=metadata,
            error=False,
        )

    def get_user(self, id: int):
        try:
            if not id:
                return Response().response(
                    status_code=400,
                    message_id="id_is_required",
                    exception="ID is required"
                )
            stmt = select(
                self.user.id,
                self.user.cpf,
                self.user.username,
                self.user.lastname,
                self.user.email,
                self.user.role,
                self.user.typecontract,
                self.employee.matricula,
            ).where(
                self.user.id == id, 
                self.user.is_deleted == False
            ).outerjoin(
                self.employee,
                self.user.id == self.employee.user_id
            )
        
            result = db.session.execute(stmt).fetchall()

            if not result:
                return Response().response(
                    status_code=404,
                    error=True,
                    message_id="user_get_not_found",
                    exception="Not found",
                )

            return Response().response(
                status_code=200,
                message_id="user_get_successful",
                data=Metadata(result).model_to_list(),
                error=False
            )
        except Exception as e:
            logdb("error", message=f"Error get user, {e}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="user_get_error",
                exception="Internal server error",
            )

    def add_user(self, data: dict):
        # hard code company_id -> 1
        try:
            if not data.get("cpf"):
                return Response().response(
                    status_code=400,
                    message_id="cpf_is_required",
                    exception="CPF is required"
                )

            password = data.get("password")
            hashed_password = generate_password_hash(password, method="scrypt") if password else None
            
            user_insert = insert(self.user).values(
                cpf=data.get("cpf"),
                username=data.get("username"),
                lastname=data.get("lastname"),
                email=data.get("email"),
                password=hashed_password,
                role=data.get("role"),
                typecontract=data.get("typecontract"),
                is_first_acess=True
            ).returning(self.user.id)
            
            user_id = db.session.execute(user_insert).scalar()
            db.session.commit()
      
            employee_insert = insert(self.employee).values(
                matricula=data.get("matricula"),
                numero_pis=data.get("numero_pis"),
                situacao_cadastro=data.get("situacao_cadastro"),
                carga_horaria_semanal=data.get("carga_horaria_semanal"),
                company_id=1,
                user_id=user_id
            ).returning(self.employee.id)
            
            employee_id = db.session.execute(employee_insert).scalar()
            db.session.commit()
            
            return Response().response(
                status_code=200,
                message_id="user_add_successful",
                metadata={"dict": data},
                data={"user_id": user_id, "employee_id": employee_id}
            )

        except IntegrityError as e:
            db.session.rollback()
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

            user = self.user.query.filter_by(id=id).first()
            employee = self.employee.query.filter_by(user_id=id).first()
            
            if not user:
                return Response().response(
                    status_code=404,
                    message_id="user_get_not_found",
                    exception="User not found"
                )

            user_fields = ['cpf', 'username', 'lastname', 'email', 'password', 'typecontract', 'is_first_acess']
            employee_fields = ['matricula', 'numero_pis', 'situacao_cadastro', 'carga_horaria_semanal', 'company_id']

            for key, value in data.items():
                if value is not None and key in user_fields:
                    if key == "password" and value:
                        value = generate_password_hash(value, method="scrypt")
                    if hasattr(user, key):
                        setattr(user, key, value)

            if employee:
                for key, value in data.items():
                    if value is not None and key in employee_fields:
                        if key == "company_id":
                            value = 1 # hardcode company_id
                        
                        if key == "numero_pis":
                            value = value.replace("-", "")[:11] if value else None
                        
                        elif key == "situacao_cadastro":
                            normalized_value = str(value).strip().lower()
                            if normalized_value in STATUS_MAP:
                                setattr(employee, key, STATUS_MAP[normalized_value])
                            continue
                        if hasattr(employee, key):
                            setattr(employee, key, value)

            db.session.commit()
            
            return Response().response(
                status_code=200,
                message_id="user_edit_successful",
                error=False
            )

        except IntegrityError as e:
            db.session.rollback()
            logdb("warning", f"Database integrity error: {str(e)}")
            return Response().response(
                status_code=400,
                message_id="database_error",
                error=True,
                exception="Database integrity error"
            )

        except ValueError as e:
            db.session.rollback()
            logdb("warning", f"Value error: {str(e)}")
            return Response().response(
                status_code=400,
                message_id="invalid_value",
                error=True,
                exception=str(e)
            )

        except Exception as e:
            print(e)
            db.session.rollback()
            logdb("error", message=f"Error editing user: {str(e)}")
            return Response().response(status_code=500, message_id="server_error", error=True, exception="Internal server error")

    def delete_user(self, id: int):
        user = self.user.query.filter_by(id=id).first()
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
        self.user.query.session.commit()
        
        user_data = user.__dict__
        user_data.pop('_sa_instance_state', None)
        return Response().response(
            status_code=200,
            message_id="user_delete_successful",
            data=user_data
        )