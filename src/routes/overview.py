from flask import Blueprint , render_template
from flask_login import login_required
from flask_login import current_user

bp_overview = Blueprint("overview", __name__, template_folder="templates")


@bp_overview.route("/home")
@login_required
def home():
    return render_template("partials/home.html")


@bp_overview.route("/dashboard")
def dashboard():
    return render_template("partials/dashboard.html")


@bp_overview.route("/profile")
def profile():
    user_id = current_user.id
    return render_template("user/profile.html", users=user_id)