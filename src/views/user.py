from flask import Blueprint, render_template


bp_user = Blueprint("users", __name__)


@bp_user.route("/login")
def login():
    return render_template("login.html")


