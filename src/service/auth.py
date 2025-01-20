class AuthUser:
    def __init__(self, id: int = None, email: str = None):
        self.id = id
        self.email = email

    def get_id(self):
        return self.id

    def is_active(self):
        return True

    def is_authenticated(self):
        return True