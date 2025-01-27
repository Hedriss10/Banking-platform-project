from src.db.pg import PgAdmin
from src.service.response import Response
from src.utils.pagination import Pagination
from src.models.rooms import RoomsModel
from src.utils.log import setup_logger
from psycopg2.errors import UniqueViolation, DuplicateObject

logger = setup_logger(__name__)


class RoomsCore:
    
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.pg = PgAdmin()
        self.models = RoomsModel(user_id=user_id)
         
    def list_rooms(self, data: dict):
        current_page, rows_per_page = int(data.get("current_page", 1)), int(data.get("rows_per_page", 10))

        if current_page < 1:  # Force variables min values
            current_page = 1
        if rows_per_page < 1:
            rows_per_page = 1

        pagination = Pagination().pagination(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=data.get("sort_by", ""),
            order_by=data.get("order_by", ""),
            filter_by=data.get("filter_by", "")
        )

        rooms = self.pg.fetch_to_dict(query=self.models.list_rooms(pagination=pagination))
        
        if not rooms:
            logger.warning(f"Rooms List Not Found.")
            return Response().response(status_code=404, error=True, message_id="rooms_list_not_found", exception="Not found", data=rooms)

        metadata = Pagination().metadata(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=pagination["sort_by"],
            order_by=pagination["order_by"],
            filter_by=pagination["filter_by"]
        )
        return Response().response(status_code=200, message_id="rooms_list_successful", data=rooms,  metadata=metadata)
     
    def add_rooms(self, data: dict):
        try:
            if not data.get("name"):
                logger.warning(f"Name is required")
                return Response().response(status_code=401, error=True, message_id="rooms_is_required", exception="Rooms Name Is Required")
            
            rooms = self.pg.execute_query(query=self.models.add_rooms(data=data))
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="rooms_add_successful", data=data, metadata={"message_id": "rooms_add_successful"})   
        except UniqueViolation:
            return Response().response(status_code=401, error=True, message_id="room_name_already_exists", data=data, metadata={"message_id": "room_name_already_exists"})  
  
    def get_rooms(self, id: int):
        try:
            rooms = self.pg.fetch_to_dict(query=self.models.get_rooms(id=id))
            if not rooms:
                logger.warning(f"Room Not Found")
                return Response().response(status_code=404, error=True, message_id="rooms_not_found", exception="Not found", data=rooms)
            return Response().response(status_code=200, error=False, message_id="rooms_add_successful", data=rooms)
        except Exception as e:
            return Response().response(status_code=409, error=False, message_id="error_processing_rooms", data=rooms, metadata={"error: error_processing_rooms"})
                 
    def edit_rooms(self, id: int, data: dict):
        try:
            if not data.get("name"):
                logger.warning(f"Rooms is Name Required.")
                return Response().response(status_code=401, error=True, message_id="name_is_required", exception="Rooms Name Is Required")
            self.pg.execute_query(query=self.models.edit_rooms(data=data, id=id))
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="rooms_update_successful") 
        except UniqueViolation:
            return Response().response(status_code=401, error=True, message_id="room_name_already_exists", data=data, metadata={"message_id": "room_name_already_exists"}) 
        
    def delete_rooms(self, id: int):
        if not id:
            logger.warning(f"Roomns Id Is Required.")
            return Response().response(status_code=401, error=True, message_id="rooms_is_required", exception="Roomns Id Is Required")
        
        self.pg.execute_query(query=self.models.delete_roooms(id=id))
        self.pg.commit()
        return Response().response(status_code=200, error=False, message_id="rooms_delete_successfull") 
    
    def rooms_user(self, id: int):
        try:
            rooms = self.pg.fetch_to_dict(query=self.models.rooms_user(id=id))
            if not rooms:
                logger.warning(f"Room Users Not Found")
                return Response().response(status_code=404, error=True, message_id="rooms_found", exception="Not found", data=rooms)
                    
            return Response().response(status_code=200, error=False, message_id="list_rooms_user_successfull", data=rooms)
        except Exception as e:
            return Response().response(status_code=400, error=False, message_id="error_rooms_user", metadata={"message_id": "error_rooms_user"})
    
    def add_rooms_user(self, data: dict):
        try:
            if not data.get("ids") or not data.get("rooms_id"):
                logger.warning("Ids and rooms_id are required.")
                return Response().response(status_code=401, error=True, message_id="ids_and_rooms_id", exception="Ids and rooms_id are required")

            check_user = self.pg.fetch_to_dict(query=self.models.check_users_rooms(user_id=data.get("ids"), rooms_id=data.get("rooms_id")))
            
            if not check_user or not isinstance(check_user, list) or "user_exists_in_room" not in check_user[0]:
                logger.error("Database query returned invalid or empty result.")
                return Response().response(status_code=500, error=True, message_id="invalid_query_result", exception="Invalid result returned from database query")

            if check_user[0]["user_exists_in_room"]:
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="user_already_in_room",
                    exception="User already exists in the room"
                )

            self.pg.execute_query(self.models.add_rooms_user(data.get("ids"), data.get("rooms_id")))
            self.pg.commit()
            return Response().response(status_code=200, message_id="user_added_to_room", exception="User successfully added to room" )

        except Exception as e:
            logger.error(f"Exception occurred: {e}")
            return Response().response(status_code=500, error=True, message_id="error_add_rooms_user", exception=str(e))
         
    def delete_rooms_user(self, data: dict, id: int):
        try:
            if not data.get("ids") and data.get("rooms_id"):
                logger.warning(f"Ids and rooms_id is Name Required.")
                return Response().response(status_code=401, error=True, message_id="ids_and_rooms_id", exception="Ids, rooms_id Is Required")
            
            self.pg.execute_query(query=self.models.delete_rooms_user(ids=data.get("ids"), rooms_id=id))
            self.pg.commit()
            return Response().response(status_code=200, error=False, message_id="rooms_users_succesfull")
        except Exception as e:
            return Response().response(status_code=500, error=True, message_id="error_delete_rooms_user", exception=str(e))