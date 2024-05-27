from external import db
from models.user import User
from werkzeug.security import generate_password_hash

new_user = User(
    user_identification=2210,
    username='Pereira',
    password=generate_password_hash('Binfae@45'),
    type_user='admin'
)

db.session.add(new_user)
db.session.commit()
