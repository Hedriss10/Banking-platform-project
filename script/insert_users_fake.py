"""
    Insert users in database with faker
"""

import random
from src.models.bsmodels import User
from src import db
from faker import Faker


fake = Faker()

# Lista de tipos de usuários para variação
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
            type_user_func=random.choice(user_types),
            typecontract="Funcionario",
            password="12345",
            email=fake.unique.email(),
            extension=fake.word(),
            extension_room=fake.random_int(min=100, max=999)
        )
        users.append(new_user)

    db.session.bulk_save_objects(users)
    db.session.commit()
    print(f"{count} usuários inseridos com sucesso!")
    
    
    
if __name__ == "__main__":
    insert_fake_users(100)