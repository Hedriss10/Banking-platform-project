from typing import Dict, List, Optional


class FlagsModels:

    def __init__(self, user_id: int, *args, **kwargs) -> None:
        self.user_id = user_id

    def add_flag(self, data: dict):
        query = f"""
            INSERT INTO flags (name, rate, created_at, is_deleted, created_by) VALUES ('{data.get("name")}', {data.get("rate")}, NOW(), FALSE, {self.user_id});
        """
        return query
    
    def list_flags(self, pagination: dict):
        query_filter = ""
        if pagination["filter_value"]:
            query_filter = f"""AND (unaccent(f.name) ILIKE unaccent('%{pagination["filter_by"]}%'))"""

        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY f.{pagination["order_by"]} {pagination["sort_by"]}"""

        query = f"""
            SELECT
                id,
                name,
                rate,
                created_by 
            FROM 
                public.flags f 
            WHERE f.is_deleted= false {query_filter}
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]}; 
        """
        return query
        
    def delete_flag(self, ids: int):
        ids_str = ', '.join(map(str, ids))
        query = f"""
            UPDATE flags 
            SET
                is_deleted = true,
                updated_at = NOW()
            WHERE id IN ({ids_str});
        """
        return query