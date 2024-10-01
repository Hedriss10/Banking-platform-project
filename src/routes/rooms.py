from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user

from src import db
from src.models.bsmodels import User, Roomns, room_user_association

bp_room = Blueprint("rooms", __name__)

@bp_room.route('/create_room', methods=['POST'])
@login_required
def create_room():
    data = request.json
    try:
        # Cria uma nova instância da sala com os dados enviados pelo front-end
        new_room = Roomns(
            create_room=data.get('create_room'),
            status=data.get('status'),
            creator_id=current_user.id
        )
        db.session.add(new_room)  # Adiciona a nova sala ao banco de dados
        db.session.commit()  # Salva a transação no banco de dados
        return jsonify({'message': 'Sala criada com sucesso!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Em caso de erro, retorna uma mensagem com status 500
    
    
@bp_room.route('/list_rooms', methods=['GET'])
@login_required
def list_rooms():
    """
        Lista todas as salas com seus respectivos vendedores associados e mostra em qual sala cada vendedor está.
    """
    rooms = Roomns.query.all()
    
    vendors = User.query.filter_by(type_user_func='Vendedor').all()
    
    rooms_data = [{
        'id': room.id,
        'create_room': room.create_room,
        'status': room.status,
        'vendors': [{'name': vendor.username, 'email': vendor.email, 'vendor_id': vendor.id} for vendor in room.users]} 
                for room in rooms]

    vendors_data = []
    for vendor in vendors:
        room_associated = None
        for room in rooms:
            if vendor in room.users:
                room_associated = room.create_room
                break
        vendors_data.append({
            'id': vendor.id,
            'name': vendor.username,
            'email': vendor.email,
            'room': room_associated
        })

    return render_template("rooms/list_rooms.html", rooms=rooms_data, vendors=vendors_data)



@bp_room.route('/list_vendors', methods=['GET'])
@login_required
def list_vendors():
    """
        Lista todos os vendedores para o front-end
    """
    vendors = User.query.filter_by(type_user_func='Vendedor').all()
    vendors_data = [{'id': vendor.id, 'name': vendor.username, 'email': vendor.email} for vendor in vendors]
    return jsonify({'vendors': vendors_data}), 200


@bp_room.route('/associate_vendors', methods=['POST'])
@login_required
def associate_vendors():
    data = request.json
    room = Roomns.query.get(data['roomId'])
    
    if room:
        try:
            for vendor_id in data['vendors']:
                vendor = User.query.get(vendor_id)
                if vendor and vendor.type_user_func == 'Vendedor':
                    if vendor not in room.users:
                        room.users.append(vendor)  # Associa o vendedor à sala
            db.session.commit()  # Salva as mudanças no banco de dados
            return jsonify({'message': 'Vendedores associados com sucesso!'}), 200
        except Exception as e:
            db.session.rollback()  # Reverte a transação em caso de erro
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Sala não encontrada.'}), 404



@bp_room.route('/delete_room/<int:room_id>', methods=['DELETE'])
@login_required
def delete_room(room_id):
    """
        Rota para apagar uma sala com base no ID
    """
    room = Roomns.query.get(room_id)
    if room:
        try:
            db.session.delete(room)
            db.session.commit()
            return jsonify({'message': 'Sala excluída com sucesso!'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Sala não encontrada.'}), 404
