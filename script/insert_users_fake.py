"""
    Insert users in database with faker
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import random
from src import db
from faker import Faker
from src import create_app
from src.models.bsmodels import User

fake = Faker()

user_types = [
    "Administrador",
    "Gerente Geral",
    "Gerente de vendas",
    "Supervisor de Vendas",
    "Vendedor",
    "Operacional",
    "Financeiro",
    "Suporte de campanha"
]

value_identification = fake.unique.random_number(digits=7, fix_len=True)

def insert_fake_users(count=100):
    users = []
    for _ in range(count):
        new_user = User(
            user_identification=f"123455678",
            username=fake.first_name(),
            lastname=fake.last_name(),
            type_user_func='Vendedor',
            typecontract="Funcionario",
            password="12345",
            email=fake.unique.email(),
        )
        users.append(new_user)

    db.session.bulk_save_objects(users)
    db.session.commit()
    print(f"{count} usuários inseridos com sucesso!")
    
    
def insert_fake_unique_user():
    # creat user unique
    new_user = User(user_identification=40028922, username='hedris', lastname='pereira', email='test@gmail.com', type_user_func='Administrador', typecontract='Funcionario', password='40028922')
    db.session.add(new_user)
    db.session.commit()


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        # insert_fake_users(100)
        insert_fake_unique_user()