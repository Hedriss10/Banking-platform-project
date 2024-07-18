from flask import Blueprint , render_template
from flask_login import login_required

bp_overview = Blueprint("overview", __name__)


@bp_overview.route("/home")
@login_required
def home():
    return render_template("partials/overview.html")

