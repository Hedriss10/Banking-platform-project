
class DataCatalogModels:
    """
    Genereate queries for datacatalog
    Manage datacatalog tables

    Returns:
        _type_: _description_
    """
    
    def __init__(self, user_id: int, *args, **kwargs) -> None:
        self.user_id = user_id

    def list_loan_operation(self, pagination: dict):
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(lo.name) ILIKE unaccent('%{pagination["filter_by"]}%'))"""

        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY tf.{pagination["order_by"]} {pagination["sort_by"]}"""

        query = f"""
            SELECT 
                id,
                initcap(trim(name)) AS name
            FROM loan_operation lo
            WHERE lo.is_deleted = false
            ORDER BY lo.id
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query

    def add_loan_operation(self, name: str):
        query = f"""
            INSERT INTO public.loan_operation (name, created_at) 
            VALUES 
            ('{name}', NOW())
            RETURNING name;    
        """
        return query

    def delete_loan_operation(self, id: int):
        query = f"""
            UPDATE public.loan_operation 
            SET 
                is_deleted=true, 
                deleted_by = {self.user_id}, 
                deleted_at = NOW()
            WHERE id = {id}
        """
        return query

    def list_benefit(self, pagination):
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(b.name) ILIKE unaccent('%{pagination["filter_by"]}%'))"""

        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY tf.{pagination["order_by"]} {pagination["sort_by"]}"""
        
        query = f"""
            SELECT 
                id,
                initcap(trim(name)) AS name
            FROM public.benefit b 
            WHERE b.is_deleted = false
            ORDER BY id ASC
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query
        
    def add_benefit(self, name: str):
        query = f"""
            INSERT INTO public.benefit (name, created_at) 
            VALUES 
            ('{name}', NOW())
            RETURNING name;
        """
        return query
        
    def delete_benefit(self, id: int):
        query = f"""
            UPDATE public.benefit 
            SET 
                is_deleted=true, 
                deleted_by = {self.user_id}, 
                deleted_at = NOW() 
            WHERE id = {id}
        """
        return query

    def list_banks(self, pagination):
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(lo.name) ILIKE unaccent('%{pagination["filter_by"]}%'))"""

        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY tf.{pagination["order_by"]} {pagination["sort_by"]}"""

        query = f"""
            SELECT
                id,
                id_bank,
                initcap(trim(name)) AS name
            FROM bank b 
            WHERE b.is_deleted = false
            ORDER by b.id
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query
    
    def add_bank(self, name: str, id_bank: int):
        query = f"""
            INSERT INTO public.bank (name, id_bank, created_at) 
            VALUES
            ('{name}', {id_bank}, NOW())
            RETURNING name;
        """
        return query
        
    def delete_bank(self, id: int):
        query = f"""
            UPDATE public.bank 
            SET 
                is_deleted=true, 
                deleted_by = {self.user_id}, 
                deleted_at = NOW()
            WHERE id = {id};
        """
        return query