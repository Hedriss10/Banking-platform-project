import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from src import db
from src.models.bsmodels import TablesFinance
from src import create_app
from sqlalchemy.sql import func
from faker import Faker


fake = Faker()

def insert_fake_tables(count=100):
    tables = []
    for _ in range(count):
        new_table = TablesFinance(
            name=fake.random_element(elements=("Cartão com Flat",  "Cartão SQ", "Credcesta")),
            type_table=fake.random_element(elements=("Refin", "Margem Livre", "Cartão/SQ")),
            table_code=fake.random_element(elements=("40028922", "3213030", "3218181")),
            start_term=fake.random_element(elements=("72", "75", "80")),
            end_term=fake.random_element(elements=("72", "75", "80")),
            rate=fake.random_element(elements=("1.5%", "2.0%", "2.5%", "3.0%")),
            is_status=False,
            banker_id=1,
            conv_id=1
        )
        tables.append(new_table)

    db.session.bulk_save_objects(tables)
    db.session.commit()
    print(f"{count} tabelas inseridas com sucesso!")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        insert_fake_tables(10)