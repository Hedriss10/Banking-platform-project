import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from src import db
from src.models.bsmodels import Proposal
from src import create_app
from sqlalchemy.sql import func
from faker import Faker

fake = Faker()

def insert_fake_proposals(count=100):
    proposals = []
    for _ in range(count):
        new_proposal = Proposal(
            creator_id=fake.random_int(min=1, max=10),  # Exemplo de ID de criador
            banker_id=fake.random_int(min=1, max=10),  # Exemplo de ID de banqueiro
            conv_id=fake.random_int(min=1, max=10),  # Exemplo de ID de convênio
            table_id=fake.random_int(min=1, max=10),
            created_at=datetime.now(),
            operation_select=fake.word(),
            matricula=fake.random_number(digits=6, fix_len=True),
            passowrd_chek="senhaexemplo",
            name=fake.first_name(),
            lastname=fake.last_name(),
            sex=fake.random_element(elements=("Masculino", "Feminino")),
            email=fake.email(),
            cpf=fake.random_number(digits=11, fix_len=True),
            naturalidade=fake.city(),
            select_state=fake.state_abbr(),
            identify_document=fake.random_number(digits=8, fix_len=True),
            organ_emissor="SSP",
            uf_emissor=fake.state_abbr(),
            name_father=fake.first_name_male(),
            name_mother=fake.first_name_female(),
            zipcode=fake.postcode(),
            address=fake.street_name(),
            address_number=fake.building_number(),
            address_complement=fake.secondary_address(),
            neighborhood=fake.city(),
            city=fake.city(),
            state_uf_city=fake.state_abbr(),
            value_salary=str(fake.random_int(min=2000, max=10000)),
            value_salaray_liquid=str(fake.random_int(min=1000, max=8000)),
            phone=fake.phone_number(),
            phone_residential=fake.phone_number(),
            phone_comercial=fake.phone_number(),
            benefit_select="Não recebeu",
            uf_benefit_select=fake.state_abbr(),
            select_banker_payment_type="Transferência",
            select_banker_payment="Banco Itau",
            receivedcardbenefit=fake.random_element(elements=("Sim", "Não")),
            agency_bank=fake.random_number(digits=4, fix_len=True),
            pix_type_key="CPF",
            agency=fake.random_number(digits=4, fix_len=True),
            agency_dv=fake.random_number(digits=1, fix_len=True),
            account=fake.random_number(digits=5, fix_len=True),
            account_dv=fake.random_number(digits=1, fix_len=True),
            type_account=fake.random_element(elements=("Corrente", "Poupança")),
            agency_op=fake.random_number(digits=3, fix_len=True),
            agency_dvop=fake.random_number(digits=1, fix_len=True),
            margem=str(fake.random_int(min=10, max=40)) + "%",
            parcela=str(fake.random_int(min=1, max=60)),
            prazo=str(fake.random_int(min=12, max=48)) + " meses",
            value_operation=int(fake.random_int(min=5000, max=100000)),
            obeserve="Observação exemplo",
            active=False,
            block=False,
            is_status=False,
            progress_check=False,
        )
        proposals.append(new_proposal)

    db.session.bulk_save_objects(proposals)
    db.session.commit()
    print(f"{count} propostas inseridas com sucesso!")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        insert_fake_proposals(100)
