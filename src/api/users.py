from flask.views import MethodView
from flask_login import current_user
from src.core.users import UserCore
from flask import jsonify, request


class UserResourceView(MethodView):
    def get(self):
        
        try:
            user_id = current_user.id
            user = UserCore(user_id=user_id).list_users(data=request.args.to_dict())
            return user
        except Exception as e:
            ...
    def post(self):
        ...
        
    def put(self):
        ...
        
    def delete(self):
        ...