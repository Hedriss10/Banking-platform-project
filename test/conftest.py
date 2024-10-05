import pytest
from src import create_app, db as _db
from src.config import TestingConfig  # Supondo que a configuração de testes esteja definida

@pytest.fixture(scope='session')
def app():
    """Instance of main Flask app."""
    app = create_app()  # Cria a aplicação normalmente

    # Carrega a configuração de testes manualmente após a criação da aplicação
    app.config.from_object(TestingConfig)
    
    with app.app_context():
        yield app

@pytest.fixture(scope='session')
def db(app):
    """Session-wide test database."""
    _db.app = app
    _db.create_all()

    yield _db

    _db.drop_all()

@pytest.fixture(scope='function')
def session(db):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    yield session

    transaction.rollback()
    connection.close()
    session.remove()

@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()
