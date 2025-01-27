import traceback
from flask import request
from flask_restx import Resource, Namespace
from flask_cors import cross_origin
from src.core.rooms import RoomsCore
from src.service.response import Response
from src.resource.swagger.factorypayloadsOperational import PaylaodFactoryRooms


rooms_ns = Namespace("rooms", description="Manage Rooms")

pagination_arguments_customer = PaylaodFactoryRooms.pagination_arguments_parser()
rooms_payload_roomms = PaylaodFactoryRooms.add_payload_room(rooms_ns) 
rooms_payload_edit_room = PaylaodFactoryRooms.edit_payload_room(rooms_ns)
rooms_payload_delete_room = PaylaodFactoryRooms.delete_associate_rooms(rooms_ns)
rooms_payload_users_associate_room = PaylaodFactoryRooms.add_asscoaite_user_rooms(rooms_ns)


@rooms_ns.route("")
class Roomns(Resource):
    
    # @jwt_required()
    @rooms_ns.doc(description="Add rooms")
    @rooms_ns.expect(rooms_payload_roomms, validate=True)
    @cross_origin()
    def post(self):
        """Add rooms"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))   
            return RoomsCore(user_id=user_id).add_rooms(data=request.get_json())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))
        
    # @jwt_required()
    @rooms_ns.doc(description="List Rooms")
    @rooms_ns.expect(pagination_arguments_customer, validate=True)
    @cross_origin()  
    def get(self):
        """List all rooms"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return RoomsCore(user_id=user_id).list_rooms(data=request.args.to_dict())

        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))


@rooms_ns.route("/<int:id>")
class RoomnsManage(Resource):
    
    # @jwt_required()
    @rooms_ns.doc(description="Get Rooms Filter by ID")
    @cross_origin()
    def get(self, id):
        """Get filter rooms by ID"""
        
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            
            return RoomsCore(user_id=user_id).get_rooms(id=id)
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))
    
    # @jwt_required()
    @rooms_ns.doc(description="Edit Romms Filter by ID")
    @rooms_ns.expect(rooms_payload_edit_room, validate=True)
    @cross_origin()
    def put(self, id):
        """Edit filter rooms by ID"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            
            return RoomsCore(user_id=user_id).edit_rooms(id=id, data=request.get_json())
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))
    
    
    # @jwt_required()
    @rooms_ns.doc(description="Delete Room Filter by ID")
    @cross_origin()
    def delete(self, id):
        """Delete filter room by ID"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))

            return RoomsCore(user_id=user_id).delete_rooms(id=id)
        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))
        

@rooms_ns.route("/rooms-users/<int:id>")
class RoomsManageUserById(Resource):
    
    # @jwt_required()
    @rooms_ns.doc(description="List Users Room")
    @cross_origin()  
    def get(self, id: int):
        """List all users_rooms associate by id room"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return RoomsCore(user_id=user_id).rooms_user(id=id)

        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))
    
    # @jwt_required()  
    @rooms_ns.doc(description="Delete Users Associate Room")
    @rooms_ns.expect(rooms_payload_delete_room, validate=True)
    @cross_origin()  
    def post(self, id: int):
        """Delete all users_rooms associate by id room"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return RoomsCore(user_id=user_id).delete_rooms_user(data=request.get_json(), id=id)

        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))
        
        
@rooms_ns.route("/rooms-users")
class RoomsManageUser(Resource):
    
    # @jwt_required()
    @rooms_ns.doc(description="Add Users Associate Room")
    @rooms_ns.expect(rooms_payload_users_associate_room, validate=True)
    @cross_origin()  
    def post(self):
        """Add all users_rooms associate by id room"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return RoomsCore(user_id=user_id).add_rooms_user(data=request.get_json())

        except Exception as e:
            return Response().response(status_code=400, error=True, message_id="something_went_wrong", exception=str(e), traceback=traceback.format_exc(e))