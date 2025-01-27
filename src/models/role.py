
class RoleModel:
    
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        
    def list_role(self, pagination: dict):
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(r.name) ILIKE unaccent('%{pagination["filter_by"]}%'))"""
        
        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY b.{pagination["order_by"]} {pagination["sort_by"]}"""
        
        query = f"""
            SELECT 
                r.id,
                initcap(trim(r.name)) as name 
            FROM 
                "role" r 
            WHERE r.is_deleted = FALSE {query_filter}
            ORDER BY r.id
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query
        
    def add_role(self, data: dict):        
        query = f"""
            INSERT INTO role(name, created_at, is_deleted) VALUES ('{data.get("name")}', NOW(), false);
        """
        return query
        
    def delete_role(self, id: int):
        query = f"""
            UPDATE public.role
            SET
                is_deleted = true
            WHERE id= {id};
        """
        return query