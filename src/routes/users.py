from flask import Blueprint, render_template
from flask.views import MethodView
from src.api.users import UserResourceView

bp_user = Blueprint("users", __name__, template_folder="templates")


class UserViewList(MethodView):
    
    def get(self):
        return render_template("user/users.html")


# manager users
bp_user.add_url_rule("/users", view_func=UserViewList.as_view("users"), methods=["GET"])
bp_user.add_url_rule("/list-users", view_func=UserResourceView.as_view("list-users"), methods=["GET"])
bp_user.add_url_rule("/user", view_func=UserResourceView.as_view("add-user"), methods=["POST"])
bp_user.add_url_rule("/user/<int:id>", view_func=UserResourceView.as_view("update-user", methods=["PUT"]))
bp_user.add_url_rule("/user/<int:id>", view_func=UserResourceView.as_view("delete-user"), methods=["DELETE"])