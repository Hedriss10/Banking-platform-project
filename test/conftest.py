import pytest
from src.app import create_app
from src.settings._base import config

@pytest.fixture(scope='session')
def app():
    """Instance of main Flask app."""
    app = create_app()
    app.config.from_object(config)
    
    with app.app_context():
        yield app

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