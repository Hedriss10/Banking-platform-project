from flask import Blueprint , render_template


bp_overview = Blueprint("overview", __name__)


@bp_overview.route("/home")
def home():
    return render_template("overview.html")