from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask.views import MethodView
from flask_login import current_user
from src.core.login import LoginCore

bp_auth = Blueprint("auth", __name__, template_folder="templates")

class AuthView(MethodView):
    
    def get(self):
        return render_template("login/login.html")

    def post(self):
        data_dict = request.form.to_dict(flat=True)
        print(data_dict)
        login_response = LoginCore().login_user(data=data_dict)
    
        if login_response[1] == 200:
            print("Usuário logado:", current_user.id)
            return redirect(url_for("overview.home"))
        
        return render_template("login/login.html")

    def logout(self):
        return redirect(url_for("auth.login"))

    def get_reset_password(self):
        return render_template("login/pagesReset.html")   
    
    def reset_password(self):
        if request.method == "POST":
            data_dict = request.form.to_dict(flat=True)
            reset_user = LoginCore().reset_password(data=data_dict)
        
            if reset_user[1] == 200:
                return redirect(url_for("auth.login"))
            else:
                return render_template("login/pagesReset.html")
        return render_template("login/pagesReset.html")

bp_auth.add_url_rule("/", view_func=AuthView.as_view("login"))
bp_auth.add_url_rule("/logout", view_func=AuthView.as_view("logout"))
bp_auth.add_url_rule("/reset-password", view_func=AuthView.as_view("reset_password"))
bp_auth.add_url_rule("/get-reset-password", view_func=AuthView.as_view("get_reset_password"))
