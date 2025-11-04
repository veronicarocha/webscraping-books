import pytest
import os
from app import create_app, db

@pytest.fixture
def app():
    """Config pra testes"""
    os.environ['SECRET_KEY'] = 'test-secret-key'
    os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret-key' 
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['DATABASE_URL_PUBLIC'] = 'sqlite:///:memory:'
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Cliente de testes"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Runner para comandos CLI"""
    return app.test_cli_runner()