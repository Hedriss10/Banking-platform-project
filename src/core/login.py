# src/core/login.py
import hashlib

from flask_jwt_extended import create_access_token
from sqlalchemy import func, outerjoin, select
from werkzeug.security import check_password_hash, generate_password_hash

from src.db.database import db
from src.models.models import Employee, User
from src.service.response import Response
from src.utils.log import logdb
from src.utils.metadata import Metadata


class LoginCore:
    
    def __init__(self, *args, **kwargs) -> None:
        self.user = User
        self.employee = Employee
        self.email = None
        self.user_id = None
    
    def compact_token(self, token):
        return hashlib.sha256(token.encode()).hexdigest()
    
    def get_login(self, data: dict):
        user = self.user.query.filter_by(email=data.get("email")).first()
        
        if not user or not user.id:
            return Response().response(message_id="user_not_found", status_code=404, error=True)
        
        self.user_id = user.id
        self.email = user.email
        password = data.get("password")
        
        join_stmt = outerjoin(
            self.user, self.employee, self.user.id == self.employee.user_id
        )
        
        stmt = select(
            self.user.id,
            self.employee.id.label("employee_id"),
            self.user.cpf,
            self.user.username,
            self.user.lastname,
            self.user.email,
            self.user.role,
            self.user.typecontract,
            self.user.is_first_acess,
            self.user.is_deleted,
            self.user.is_acctive,
            self.employee.matricula,
            self.employee.numero_pis,
            self.employee.situacao_cadastro,
            self.employee.carga_horaria_semanal,
            self.user.is_admin,
            self.user.is_block,
            self.user.is_comission,
            func.to_char(self.user.create_at, 'YYYY-MM-DD').label("create_at")
        ).select_from(join_stmt).where(self.user.id == self.user_id)
        
        result = db.session.execute(stmt).fetchone()
        
        if not password:
            return Response().response(message_id="password_not_user", status_code=400, error=True)
        
        is_valid = check_password_hash(user.password, password)
        
        if is_valid:
            access_token = create_access_token(identity={"id": self.user_id, "email": self.email})
            db.session.commit()
            return Response().response(
                message_id="user_logged_in_successfully", 
                status_code=200, error=False, 
                data=Metadata(result).model_to_list(), 
                metadata={'access_token': self.compact_token(access_token)})
        else:
            logdb("warning", message="Incorrect password")
            return Response().response(message_id="incorrect_password", status_code=401, error=True)
        
    def reset_password_authorization(self, data: dict):
        try:
            new_password = generate_password_hash(password="123@bs", method="scrypt")
            id = self.user.query.filter_by(id=data.get("id")).update({"password": new_password, "updated_at": func.now()})
            db.session.commit()
            return Response().response(message_id="reset_successfully", status_code=200, error=False, data=id)
        except Exception as e:
            logdb("error", message=str(e))
            return Response().response(message_id="resert_password_error", status_code=401, error=True)