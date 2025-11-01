# File: /missing-person-ai/missing-person-ai/tests/conftest.py

import pytest

@pytest.fixture(scope='session')
def test_client():
    from app import create_app

    app = create_app()
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client

@pytest.fixture(scope='session')
def init_database():
    from app import db
    db.create_all()

    yield db  # This is where the testing happens

    db.drop_all()