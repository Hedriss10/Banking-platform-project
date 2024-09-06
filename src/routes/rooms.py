from flask_sqlalchemy import pagination
from flask import (Blueprint, render_template, url_for, jsonify, abort, redirect, request, current_app, flash)
from flask_login import login_required, current_user 
from src import db
from src.models.user import User
from src.models.rooms import Roomns

bp_room = Blueprint("rooms", __name__)


@bp_room.route("/create-at")
@login_required
def room():
    selles = User.query.filter_by(type_user_func='Vendedor').all()
    roomns = Roomns.query.all() 

    return render_template("rooms/manage_create_rooms.html", users=selles, rooms=roomns)


@bp_room.route('/create_room', methods=['POST'])
def create_room():
    data = request.json
    try:
        new_room = Roomns(
            create_room=data.get('create_room'),
            status=data.get('status'),
            creator_id=current_user.id
        )
        db.session.add(new_room)
        db.session.commit()
        return jsonify({'message': 'Sala criada com sucesso!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@bp_room.route('/list_rooms', methods=['GET'])
def list_rooms():
    """
        Function list rooms for active associete users
    """
    rooms = Roomns.query.all()
    user = User.query.all()
    rooms_data = [{
        'id': room.id,
        'create_room': room.create_room,
        'status': room.status,
        'vendors': [{'name': user.username, 'email': user.email} for user in room.users]
    } for room in rooms]

    return render_template("rooms/list_rooms.html", room=rooms_data, user=user)



@bp_room.route('/list_vendors', methods=['GET'])
def list_vendors():
    vendors = User.query.filter_by(type_user_func='Vendedor').all()
    vendors_data = [{'id': vendor.id, 'name': vendor.username, 'email': vendor.email} for vendor in vendors]
    return jsonify({'vendors': vendors_data}), 200


@bp_room.route('/associate_vendors', methods=['POST'])
def associate_vendors():
    data = request.json
    room = Roomns.query.get(data['roomId'])
    if room:
        for vendor_id in data['vendors']:
            vendor = User.query.get(vendor_id)
            if vendor and vendor.type_user_func == 'Vendedor':
                room.users.append(vendor)
        db.session.commit()
        return jsonify({'message': 'Vendors successfully associated!'}), 200
    return jsonify({'error': 'Room not found.'}), 404

