from src.models.token import ModelToken
from src.db.pg import PgAdmin
from src.service.response import Response
from src.utils.pagination import Pagination
from src.utils.log import setup_logger
from psycopg2.errors import UniqueViolation


logger = setup_logger(__name__)



class CoreToken:
    
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.models = ModelToken(user_id=user_id)
        self.pg = PgAdmin()
        
    def get_token(self, id: int):
        try:
            token = self.pg.fetch_to_dict(query=self.models.get_toke_chek_user(id=id))
            if not token:
                logger.warning("Token not found")
                return Response().response(status_code=200, message_id="get_token_not_found", data=token, exception="Token not found")
                
            return Response().response(status_code=200, message_id="get_token_sucessfully", data=token)
        except Exception as e:
            logger.error(f"Error log get token", exc_info=True)
            return Response().response(status_code=401, message_id="erro_get_token", data=token) 