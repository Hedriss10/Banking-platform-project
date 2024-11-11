from src import db
from src.models.bsmodels import Roomns, User

class RoomsControllers:
    
    def __init__(self, current_user):
        self.current_user = current_user

    def create_room_controller(self, data, creator_id):
        try:
            new_room = Roomns(
                create_room=data.get('create_room'),
                status=data.get('status'),
                creator_id=creator_id
            )
        
            db.session.add(new_room)
            db.session.commit()
            
            return {'success': True, 'message': 'Sala criada com sucesso!'}, 200

        except Exception as e:
            db.session.rollback()
            return {'error': True, 'message': f'Erro ao criar sala: {str(e)}'}, 500
    
    def list_rooms_controller(self):
        try:
            rooms = Roomns.query.all()
            vendors = User.query.filter_by(type_user_func='Vendedor').all()

            rooms_data = [{
                'id': room.id,
                'create_room': room.create_room,
                'status': room.status,
                'vendors': [{'name': vendor.username, 'email': vendor.email, 'vendor_id': vendor.id} for vendor in room.users]
            } for room in rooms]

            vendors_data = []
            for vendor in vendors:
                room_associated = next((room.create_room for room in rooms if vendor in room.users), None)
                vendors_data.append({
                    'id': vendor.id,
                    'name': vendor.username,
                    'email': vendor.email,
                    'room': room_associated
                })

            return {'rooms': rooms_data, 'vendors': vendors_data}, 200

        except Exception as e:
            return {'error': True, 'message': f'Erro ao listar salas: {str(e)}'}, 500
        
    def list_vendors_controller(self):
        try:
            vendors = User.query.filter_by(type_user_func='Vendedor').all()            
            vendors_data = [{'id': vendor.id, 'name': vendor.username, 'email': vendor.email} for vendor in vendors]
            return {'vendors': vendors_data}, 200

        except Exception as e:
            return {'error': True, 'message': f'Erro ao listar vendedores: {str(e)}'}, 500

    def associate_vendors_controller(self, data):
        try:
            room = Roomns.query.get(data['roomId'])
            if not room:
                return {'error': True, 'message': 'Sala não encontrada.'}, 404

            for vendor_id in data['vendors']:
                vendor = User.query.get(vendor_id)
                if vendor and vendor.type_user_func == 'Vendedor':
                    if vendor not in room.users:
                        room.users.append(vendor)
            
            db.session.commit()
            return {'success': True, 'message': 'Vendedores associados com sucesso!'}, 200

        except Exception as e:
            db.session.rollback()
            return {'error': True, 'message': f'Erro ao associar vendedores: {str(e)}'}, 500
        
    def delete_room_controller(self, room_id):
        
        try:
            room = Roomns.query.get(room_id)
            if not room:
                return {'error': True, 'message': 'Sala não encontrada.'}, 404

            db.session.delete(room)
            db.session.commit()
            
            return {'success': True, 'message': 'Sala excluída com sucesso!'}, 200

        except Exception as e:
            db.session.rollback()
            return {'error': True, 'message': f'Erro ao excluir sala: {str(e)}'}, 500
