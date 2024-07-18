from flask import Blueprint , render_template, request, redirect, url_for
from flask_login import login_required
from flask_login import current_user
from src import db 
from flask import jsonify
from datetime import datetime
from ..models.hourpoint import Point, VocationBs


bp_point_hour = Blueprint("hourpoint", __name__)

@bp_point_hour.route("/point", methods=['GET'])
@login_required
def get_point_hour():
    return render_template("point/hourpoint.html")


@bp_point_hour.route("/registerpoint", methods=['POST'])
@login_required
def point_hour():
    day_hour_str = request.form['day_hour']
    type = request.form['type']
    user_id = current_user.id
    
    try:
        day_hour = datetime.strptime(day_hour_str, '%d/%m/%Y, %H:%M')
    except Exception as e:
        print(f"{e}")
        return jsonify({'error': 'Invalid date format'}), 400

    new_point = Point(user_id=user_id, day_hour=day_hour, type=type)
    db.session.add(new_point)
    db.session.commit()
    return redirect(url_for("overview.home"))