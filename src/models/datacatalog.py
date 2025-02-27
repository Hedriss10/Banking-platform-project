
class DataCatalogModels:
    
    def __init__(self, user_id: int, *args, **kwargs) -> None:
        self.user_id = user_id

    # loan operation
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

    def get_loan_operation(self, id: int):
        query = f"""
            SELECT
                id,
                initcap(trim(name)) AS name
            FROM loan_operation lo
            WHERE lo.id = {id}
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

    def edit_loan_operation(self, id: int, name: str):
        query = f"""
            UPDATE public.loan_operation lo SET name='{name}' WHERE lo.id = {id};
        """
        return query

    def delete_loan_operation(self, id: int):
        query = f"""
            UPDATE public.loan_operation lo SET is_deleted=true WHERE lo.id = {id}
        """
        return query

    # list rank tables
    def list_rank_tables(self, pagination: dict):
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(tf.table_code) ILIKE unaccent('%{pagination["filter_by"]}%')) OR (unaccent(b.name) ILIKE unaccent('%{pagination["filter_by"]}%'))"""

        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY tf.{pagination["order_by"]} {pagination["sort_by"]}"""

        query = f"""
            SELECT
                tf.id as id_table,
                b.id as banker_id,
                fa.id as financial_agreements_id,
                b.name,
                fa.name as financial_agreements,
                tf.name as table,
                tf.table_code as table_code,
                tf.start_term,
                tf.end_term
            FROM tables_finance tf 
            INNER JOIN bankers b ON b.id = tf.banker_id 
            INNER JOIN financial_agreements fa ON fa.id = tf.financial_agreements_id 
            WHERE tf.is_deleted = false {query_filter}
            ORDER BY tf.id
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query
    
    # benefit
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
        
    def edit_benefit(self, id: int, name: str):
        query = f"""
            UPDATE public.benefit b SET name='{name}' WHERE b.id = {id};
        """
        return query
        
    def get_benefit(self, id: int):
        query = f"""
            SELECT
                id,
                initcap(trim(name)) AS name
            FROM public.benefit AS b
            WHERE b.is_deleted = false and b.id = {id}
        """
        return query
        
    def delete_benefit(self, id: int):
        query = f"""
            UPDATE public.benefit AS b SET is_deleted=True AND b.id = {id}
        """
        return query
        
    # banks
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

    def get_bank(self, id: int): 
        query = f"""
            SELECT 
                id_bank,
                initcap(trim(name)) AS name
            FROM bank b 
            WHERE b.is_deleted = false AND b.id = {id}
            ORDER by b.id
        """
        return query
        
    def edit_bank(self, id: int, name: str):
        query = f"""
            UPDATE public.bank b SET name='{name}' WHERE b.id_bank = {id};
        """
        return query
        
    def delete_bank(self, id: int):
        query = f"""
            UPDATE public.bank b SET is_deleted=true WHERE b.id_bank = {id};
        """
        return query
    
    # list tables register in database of forms proposal
    def list_tables(self, pagination: dict):
        query_filter = ""
        if pagination["filter_by"]:
            query_filter = f"""AND (unaccent(tf.table_code) ILIKE unaccent('%{pagination["filter_by"]}%'))"""

        query_order_by = ""
        if pagination["sort_by"] and pagination["order_by"]:
            query_order_by = f"""ORDER BY tf.{pagination["order_by"]} {pagination["sort_by"]}"""
        
        query = f"""
            SELECT 
                tf.id as tables_finance_id,
                tf.name,
                tf.type_table,
                tf.table_code,
                tf.start_term,
                tf.end_term,
                tf.rate,
                tf.banker_id,
                tf.financial_agreements_id
            FROM tables_finance tf
            LEFT JOIN bankers b on b.id = tf.id
            LEFT JOIN financial_agreements fa on fa.id = tf.financial_agreements_id 
            WHERE tf.is_deleted = false {query_filter}
            ORDER BY tf.id
            OFFSET {pagination["offset"]} LIMIT {pagination["limit"]};
        """
        return query