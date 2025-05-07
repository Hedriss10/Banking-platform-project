import pytest

from src.app import create_app
from src.settings._base import config_by_name, flask_env


@pytest.fixture(scope='session')
def app():
    """Instance of main Flask app."""
    app = create_app()

    config_class = config_by_name[flask_env]
    app.config.from_object(config_class)
    
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