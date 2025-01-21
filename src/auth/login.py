from flask import Blueprint, request, render_template, redirect, url_for
from flask.views import MethodView
from flask_login import current_user
from src.core.login import LoginCore

bp_auth = Blueprint("auth", __name__, template_folder="templates")

class AuthView(MethodView):
    def get(self):
        return render_template("login/login.html")

    def post(self):
        login_response = LoginCore().login_user(data=request.get_json())

        if login_response:
            return login_response
        else:
            return redirect(url_for("auth.login"))

    def logout(self):
        return redirect(url_for("auth.login"))


class ResetView(MethodView):
    
    def get(self):
        return render_template("login/pagesReset.html")
    
    def post(self):
        reset_user = LoginCore().reset_password(data=request.get_json())
        
        if reset_user:
            return reset_user
        else:
            return render_template("login/pagesReset.html")

bp_auth.add_url_rule("/login", view_func=AuthView.as_view("login"), methods=["GET", "POST"])
bp_auth.add_url_rule("/logout", view_func=AuthView.as_view("logout"))
bp_auth.add_url_rule("/resetpassword", view_func=ResetView.as_view("get_reset"), methods=["GET"])
bp_auth.add_url_rule("/new-restpassword", view_func=ResetView.as_view("reset_password"), methods=["POST"])