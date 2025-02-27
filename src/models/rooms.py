class RoomsModel:

    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id

    def list_rooms(self, pagination: dict):
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(r.name) ILIKE unaccent('%{pagination["filter_by"]}%'))"""
        
        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY b.{pagination["order_by"]} {pagination["sort_by"]}"""
        
        query = f"""
            SELECT
                id,
                initcap(trim(r.name)) as name
            FROM 
                rooms r 
            WHERE r.is_deleted = false {query_filter}
            ORDER BY id
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query

    def get_rooms(self, id: int):
        query = f"""
            SELECT
                id,
                initcap(trim(r.name)) as name
            FROM 
                rooms r 
            WHERE r.is_deleted = false and r.id = {id}
            ORDER BY id
        """
        return query

    def add_rooms(self, data: dict):
        query = f"""
            INSERT INTO rooms (name, created_at, is_deleted) VALUES ('{data.get("name")}', NOW(), false);
        """
        return query

    def update_rooms(self, id: int, data: dict):
        query = f"""
            UPDATE rooms SET name='{data.get("name")}' where id = {id}
        """
        return query

    def delete_roooms(self, id: int):
        query = f"""
            UPDATE rooms SET is_deleted = true where id = {id}
        """
        return query

    def rooms_user(self, id: int, pagination: dict):
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(r.name) ILIKE unaccent('%{pagination["filter_by"]}%')) OR (unaccent(u.username) ILIKE unaccent('%{pagination["filter_by"]}%'))"""
        
        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY b.{pagination["order_by"]} {pagination["sort_by"]}"""
            
        query = f"""
            SELECT
                u.id,
                r.name as room_name,
                initcap(trim(u.username)) as name,
                initcap(trim(u.role)) as role
            FROM 
                rooms r
                INNER JOIN public.rooms_users ru on ru.rooms_id = r.id
                INNER JOIN public.user u on ru.user_id = u.id
            WHERE r.id = {id} AND r.is_deleted = false AND u.is_deleted = false {query_filter}
            {query_order_by}
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query
    
    def add_rooms_user(self, ids: list[int], rooms_id: list[int]):
        room_id = rooms_id[0]

        values = ', '.join(
            f"({user_id}, NOW(), {room_id}, false)" for user_id in ids
        )

        query = f"""
            INSERT INTO rooms_users (user_id, created_at, rooms_id, is_deleted)
            VALUES {values};
        """
        return query
    
    def check_users_rooms(self, rooms_id: int, user_id: list[int]):
        user_ids_str = ",".join(map(str, user_id))
        rooms_id_str = ",".join(map(str, rooms_id))
        query = f"""
            SELECT 
                CASE
                    WHEN EXISTS (
                        SELECT 
                            1
                        FROM 
                            rooms_users ru
                        WHERE ru.user_id IN ({user_ids_str}) AND ru.rooms_id = {rooms_id_str}
                    ) THEN TRUE
                    ELSE FALSE
                END AS user_exists_in_room;
        """
        return query
    
    def delete_rooms_user(self, ids: list[int], rooms_id: int):
        conditions = ' OR '.join(
            f"(user_id = {user_id} AND rooms_id = {rooms_id})" for user_id in ids
        )
        query = f"""
            DELETE FROM rooms_users
            WHERE {conditions};
        """
        return query