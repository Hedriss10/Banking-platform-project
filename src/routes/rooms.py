from flask import Blueprint, render_template, jsonify, request
from flask import flash, redirect, url_for
from flask_login import login_required, current_user


from src.controllers.rooms import RoomsControllers

bp_room = Blueprint("rooms", __name__)

@bp_room.route('/create_room', methods=['POST'])
@login_required
def create_room():
    """
        Create rooms
    Returns:
        _type_: create rooms
    """
    
    data = request.get_json()
    response, status_code = RoomsControllers(current_user=current_user).create_room_controller(data, current_user.id)
    return jsonify(response), status_code

@bp_room.route('/list_rooms', methods=['GET'])
@login_required
def list_rooms():
    """
        list rooms
    Returns:
        _type_: [list rooms]
    """

    response, status_code = RoomsControllers(current_user=current_user).list_rooms_controller()
    
    if status_code == 200:
        return render_template("rooms/list_rooms.html", rooms=response['rooms'], vendors=response['vendors'])
    else:
        flash(response['message'], 'error')
        return redirect(url_for('some_error_page'))

@bp_room.route('/list_vendors', methods=['GET'])
@login_required
def list_vendors():
    """
        List vendors
    Returns:
        _type_: list vendors for frontend
    """
    response, status_code = RoomsControllers(current_user=current_user).list_vendors_controller()
    return jsonify(response), status_code

@bp_room.route('/associate_vendors', methods=['POST'])
@login_required
def associate_vendors():
    """
        Associate vendors 
    Returns:
        _type_: return associate vendors
    """
    
    data = request.get_json()
    response, status_code = RoomsControllers(current_user=current_user).associate_vendors_controller(data)
    return jsonify(response), status_code

@bp_room.route('/delete_room/<int:room_id>', methods=['DELETE'])
@login_required
def delete_room(room_id):
    """Route to delete a room by its ID"""
    response, status_code = RoomsControllers().delete_room_controller(room_id)
    return jsonify(response), status_code