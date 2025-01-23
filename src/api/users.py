from flask.views import MethodView
from flask_login import current_user
from src.core.users import UserCore
from flask import jsonify, request
from src.service.log import setup_logger

logger = setup_logger(__name__)

class UserResourceView(MethodView):
    def get(self):
        
        try:
            user_id = current_user.id
            user = UserCore(user_id=user_id).list_users(data=request.args.to_dict())
            return user
        except Exception as e:
            ...
    def post(self):
        try:
            user = UserCore().add_user(data=request.get_json())
            return user
        except Exception as e:
            logger.error(f"Error adding user: {e}", exc_info=True)
        
    def put(self):
        ...
        
    def delete(self):
        ...