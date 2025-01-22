from flask import Blueprint, request, render_template, redirect, url_for
from flask.views import MethodView
from flask_login import current_user
from src.core.ex1 import UserCore

from src.models.user import User
from flask import jsonify

bp_user = Blueprint("users", __name__, template_folder="templates")

class UserView(MethodView):
    
    def get(self):
        user_id = current_user.id
        data, status_code = UserCore(user_id=user_id).list_users(data=request.args.to_dict())

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
            return jsonify(data), status_code

        if status_code == 200:
            return render_template("user/users.html", users=data['users'], pagination=data['pagination'])
        else:
            return jsonify({'message': data['message']}), status_code
    
    def post(self):
        ...
        
    def put(self):
        ...
        
    def delete(self):
        ...
        
        
bp_user.add_url_rule("/users", view_func=UserView.as_view("users"), methods=["GET"])
bp_user.add_url_rule("/addusers", view_func=UserView.as_view("addusers"), methods=["POST"])
bp_user.add_url_rule("/updateusers/<int:id>", view_func=UserView.as_view("updateusers", methods=["PUT"]))
bp_user.add_url_rule("/deleteusers/<int:id>", view_func=UserView.as_view("deleteusers"), methods=["DELETE"])

