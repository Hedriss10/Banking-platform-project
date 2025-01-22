from flask_login import UserMixin

class UserAuth(UserMixin):
    def __init__(
        self,
        id: int,
        username: str,
        email: str,
        password: str,
        role: str,
        session_token: str,
        is_acctive: bool = True,
        is_block: bool = False,
        is_deleted: bool = False,
        *args, **kwargs
    ):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.role = role
        self.session_token = session_token
        self.is_acctive = is_acctive
        self.is_block = is_block
        self.is_deleted = is_deleted

    def get_id(self):
        return str(self.id)
    
    def get_role(self):
        return str(self.role)
