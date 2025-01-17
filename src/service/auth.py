class AuthUser:
    def __init__(self, id, email):
        self.id = id
        self.email = email

    def is_active(self):
        return True

    def is_authenticated(self):
        return True