from flask import Blueprint , render_template, jsonify
from flask_login import login_required, current_user
from src import check_session_token
from src.controllers.overview import OverviewControllers

bp_overview = Blueprint("overview", __name__, template_folder="templates")


@bp_overview.route("/home")
@login_required
@check_session_token
def home():
    """Function for process overview system"""
    return render_template("partials/home.html")

@bp_overview.route("/dashboard")
@login_required
def dashboard():
    """Function for processing dash board"""
    return render_template("partials/dashboard.html")

@bp_overview.context_processor
def inject_user():
    return dict(current_user=current_user)

@bp_overview.route("/profile")
@login_required
def profile():
    """Route to render the user's profile page"""
    response = OverviewControllers(current_user=current_user).get_user_profile(current_user.id)
    
    if isinstance(response, dict) and 'error' in response:
        return jsonify(response), 404
    
    return render_template("user/profile.html", users=response)