from itsdangerous import URLSafeSerializer

SECRET_KEY = "maisbs"

def generate_token(id):
    serializer = URLSafeSerializer(SECRET_KEY)
    return serializer.dumps(id)

def validate_token(token):
    serializer = URLSafeSerializer(SECRET_KEY)
    try:
        return serializer.loads(token)
    except Exception:
        return None