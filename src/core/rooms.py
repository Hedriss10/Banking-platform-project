# src/core/rooms.py

from datetime import datetime

from psycopg2.errors import UniqueViolation
from sqlalchemy import func, join, or_, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import aliased

from src.db.database import db
from src.models.models import Rooms, RoomsUsers, User
from src.service.response import Response
from src.utils.log import logdb
from src.utils.metadata import Metadata
from src.utils.pagination import Pagination


class RoomsCore:

    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.users = User
        self.rooms = Rooms
        self.rooms_users = RoomsUsers

    def list_rooms(self, data: dict):
        current_page = int(data.get("current_page", 1))
        rows_per_page = int(data.get("rows_per_page", 10))

        if current_page < 1:
            current_page = 1
        if rows_per_page < 1:
            rows_per_page = 1

        pagination = Pagination().pagination(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=data.get("sort_by", ""),
            order_by=data.get("order_by", ""),
            filter_by=data.get("filter_by", ""),
            filter_value=data.get("filter_value", "")
        )

        Room = aliased(self.rooms)

        stmt = select(Room.id, Room.name).where(Room.is_deleted == False)

        # Filtro dinâmico com ILIKE + unaccent
        if pagination["filter_value"]:
            filter_value = f"%{pagination['filter_value']}%"
            stmt = stmt.where(
                or_(
                    func.unaccent(Room.name).ilike(func.unaccent(filter_value))
                )
            )

        # Ordenação dinâmica
        if pagination["order_by"] and pagination["sort_by"]:
            sort_column = getattr(Room, pagination["order_by"], None)
            if sort_column:
                if pagination["sort_by"] == "asc":
                    stmt = stmt.order_by(sort_column.asc())
                else:
                    stmt = stmt.order_by(sort_column.desc())
        else:
            stmt = stmt.order_by(Room.id.desc())

        # Paginação
        offset = pagination["offset"]
        limit = pagination["limit"]

        paginated_stmt = stmt.offset(offset).limit(limit)
        results = db.session.execute(paginated_stmt).fetchall()

        if not results:
            return Response().response(
                status_code=404, 
                error=True, 
                message_id="rooms_list_not_found", 
                exception="Not found"
            )
        
        total = db.session.execute(
            select(func.count()).select_from(Room).where(Room.is_deleted == False)
        ).scalar()

        metadata = Pagination().metadata(
            current_page=current_page,
            rows_per_page=rows_per_page,
            sort_by=pagination["sort_by"],
            order_by=pagination["order_by"],
            filter_by=pagination["filter_by"],
            filter_value=pagination["filter_value"],
            total=total
        )

        return Response().response(
            status_code=200, 
            message_id="rooms_list_successful", 
            data=Metadata(results).model_to_list(),
            metadata=metadata
        )

    def add_rooms(self, data: dict):
        try:
            if not data.get("name"):
                return Response().response(
                    status_code=401, 
                    error=True, 
                    message_id="rooms_is_required", 
                    exception="Rooms Name Is Required"
                )
            rooms = self.rooms(name=data.get("name"), 
                is_deleted=False, is_inactive=False, is_status=False, created_at=func.now()
            )
            self.rooms.query.session.add(rooms)
            self.rooms.query.session.commit()
            
            return Response().response(
                status_code=200, 
                error=False, 
                message_id="rooms_add_successful",
            )
        except UniqueViolation:
            return Response().response(
                status_code=401, 
                error=True, 
                message_id="room_name_already_exists", 
                data=data
            )

    def get_room(self, id: int):
        try:
            stmt = select(
                self.rooms.id,
                func.initcap(func.trim(self.rooms.name)).label('name')
            ).where(self.rooms.id == id, self.rooms.is_deleted == False)

            result = db.session.execute(stmt).fetchone()

            if not result:
                return Response().response(
                    status_code=404, 
                    error=True, 
                    message_id="rooms_not_found", 
                    exception="Not found", 
                    data=None
                )

            return Response().response(
                status_code=200, 
                error=False, 
                message_id="rooms_fetch_successful", 
                data=Metadata(result).model_to_dict()
            )

        except Exception as e:
            logdb("error", message=f"Error processing rooms: {e}")
            return Response().response(
                status_code=409, 
                error=True, 
                message_id="error_processing_rooms", 
                exception=str(e),
                data=None
            )

    def update_rooms(self, id: int, data: dict):
        try:
            if not data.get("name"):
                return Response().response(
                    status_code=401, 
                    error=True, 
                    message_id="name_is_required", 
                    exception="Rooms Name Is Required"
                )

            rooms = self.rooms.query.filter_by(id=id, is_deleted=False).first()
            rooms.name = data.get("name")
            self.rooms.query.session.commit()
            
            return Response().response(
                status_code=200, 
                error=False, 
                message_id="rooms_update_successful"
            )
        except UniqueViolation:
            return Response().response(
                status_code=401, 
                error=True, 
                message_id="room_name_already_exists", 
                data=data, 
                metadata={"message_id": "room_name_already_exists"}
            )

    def delete_rooms(self, id: int):
        if not id:
            return Response().response(
                status_code=401, 
                error=True, 
                message_id="rooms_is_required", 
                exception="Roomns Id Is Required"
            )

        rooms = self.rooms.query.filter_by(id=id, is_deleted=False).first()
        if not rooms:
            return Response().response(
                status_code=404, 
                error=True, 
                message_id="rooms_not_found", 
                exception="Not found", 
                data=rooms
            )

        rooms.is_deleted = True
        self.rooms.query.session.commit()
        return Response().response(status_code=200, error=False, message_id="rooms_delete_successfull")

    def rooms_user(self, id: int, data: dict):
        try:
            current_page = max(int(data.get("current_page", 1)), 1)
            rows_per_page = max(int(data.get("rows_per_page", 10)), 1)

            pagination = Pagination().pagination(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=data.get("sort_by", ""),
                order_by=data.get("order_by", ""),
                filter_by=data.get("filter_by", ""),
            )

            offset = pagination["offset"]
            limit = pagination["limit"]

            # JOIN entre rooms, rooms_user e users
            join_stmt = join(
                self.rooms, self.rooms_users, self.rooms.id == self.rooms_users.rooms_id
            ).join(
                self.users, self.rooms_users.user_id == self.users.id
            )

            stmt = (
                select(
                    self.users.id.label("id"),
                    func.initcap(func.trim(self.users.username)).label("name"),
                    func.initcap(func.trim(self.users.role)).label("role"),
                    self.rooms.name.label("room_name")
                )
                .select_from(join_stmt)
                .where(
                    self.rooms.id == id,
                    self.rooms.is_deleted == False,
                    self.users.is_deleted == False,
                    self.users.is_block == False,
                    self.rooms_users.is_deleted == False
                )
                .offset(offset)
                .limit(limit)
            )

            result = db.session.execute(stmt).fetchall()

            if not result:
                return Response().response(
                    status_code=404,
                    error=True,
                    message_id="rooms_users_not_found",
                    exception="Not found",
                    data=[]
                )

            return Response().response(
                status_code=200,
                error=False,
                message_id="list_rooms_user_successfull",
                data=Metadata(result).model_to_list()
            )

        except Exception as e:
            logdb("error", message=f"Erro rooms_user: {e}")
            return Response().response(
                status_code=400,
                error=True,
                message_id="error_rooms_user",
                exception=str(e),
                data=[]
            )

    def add_rooms_user(self, data: dict):
        try:
            ids = data.get("ids")
            room_id = data.get("rooms_id")
            if isinstance(room_id, list):
                room_id = room_id[0]

            if not ids or not room_id:
                return Response().response(
                    status_code=401,
                    error=True,
                    message_id="ids_and_rooms_id",
                    exception="Ids and rooms_id are required"
                )

            values = [
                {
                    "user_id": user_id,
                    "rooms_id": room_id,
                    "created_at": datetime.utcnow(),
                    "is_deleted": False
                }
                for user_id in ids
            ]

            # Monta o INSERT com ON CONFLICT DO NOTHING
            stmt = insert(self.rooms_users).values(values)
            stmt = stmt.on_conflict_do_nothing(index_elements=["user_id", "rooms_id"])

            db.session.execute(stmt)
            db.session.commit()

            return Response().response(
                status_code=200,
                message_id="user_add_to_room",
                error=False
            )

        except Exception as e:
            db.session.rollback()
            logdb("error", message=f"Error adding user to room: {e}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_add_rooms_user",
                exception=str(e)
            )

    def delete_rooms_user(self, data: dict, id: int):
        try:
            user_ids = data.get("ids")

            if not user_ids:
                return Response().response(
                    status_code=401,
                    error=True,
                    message_id="ids_and_rooms_id",
                    exception="Ids and rooms_id are required"
                )

            stmt = (
                update(self.rooms_users)
                .where(
                    self.rooms_users.user_id.in_(user_ids),
                    self.rooms_users.rooms_id == id
                )
                .values(is_deleted=True)
            )
            db.session.execute(stmt)
            db.session.commit()

            return Response().response(
                status_code=200,
                error=False,
                message_id="rooms_user_delete_successful"
            )

        except Exception as e:
            db.session.rollback()
            logdb("error", message=f"Erro ao deletar rooms_user: {e}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_delete_rooms_user",
                exception=str(e)
            )

