import hashlib
from src.models.login import LoginModels
from src.db.pg import PgAdmin
from src.service.response import Response
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token
from src.utils.log import setup_logger

logger = setup_logger(__name__)


class LoginCore:

    def __init__(self, *args, **kwargs) -> None:
        self.pg = PgAdmin()
        self.user_id = None
        self.email = None
        self.model = LoginModels(email=self.email, user_id=self.user_id)

    def compact_token(self, token):
        return hashlib.sha256(token.encode()).hexdigest()

    def get_login(self, data: dict):
        
        user = self.pg.fetch_to_dict(query=self.model.get_user_login(data.get("cpf")))
        
        if not user or not user[0]['id']:
            logger.warning("User not found")
            return Response().response(message_id="user_not_found", status_code=404, error=True)

        self.user_id = user[0]["id"]
        self.email = user[0]["email"]
        password = data.get("password")

        # info
        user_info = self.pg.fetch_to_dict(query=self.model.get_user_list_info(id=self.user_id))

        if not password:
            logger.warning("Password not user")
            return Response().response(message_id="password_not_user", status_code=400, error=True)

        is_valid = check_password_hash(user[0]["password"], password)
        if is_valid:
            access_token = create_access_token(identity={"id": self.user_id, "email": self.email})
            self.pg.execute_query(query=self.model.add_session_token(token=self.compact_token(token=access_token), id=self.user_id))
            self.pg.commit()
            
            return Response().response(message_id="user_logged_in_successfully", status_code=200, error=False, data=user_info, metadata={'access_token': self.compact_token(access_token)})
        else:
            logger.warning("Incorrect password")
            return Response().response(message_id="incorrect_password", status_code=401, error=True)

    def reset_password_authorization(self, data: dict, user_id: int):
        try:
            new_password = generate_password_hash(password="123@bs", method="scrypt")
            id = self.pg.fetch_to_dict(query=self.model.reset_password_master(id=data.get("id"), password=new_password, user_id=user_id))
            if not id:
                return Response().response(message_id="id_not_found", status_code=404, error=True)

            return Response().response(message_id="reset_successfully", status_code=200, error=False, data=id)

        except Exception as e:
            return Response().response(message_id="resert_password_error", status_code=401, error=True)