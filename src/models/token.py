
class ModelToken:
    
    def __init__(self, user_id: int, *agrs, **kwargs):
        self.user_id = user_id
        
    def get_toke_chek_user(self, id: int):
        query = f"""
            select id, session_token from public.user u where u.id = {id}; 
        """
        return query
    
    
    