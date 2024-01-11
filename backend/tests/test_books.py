from unittest.mock import Mock
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask import Flask, json
from flask_login import LoginManager
import pytest
from api.books import init_books_module
from flask.testing import FlaskClient
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from api.auth import init_auth_module

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'

    # Initialize PyMongo with a mock
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/testdb'
    app.mongo = PyMongo(app, uri=app.config['MONGO_URI'])
    
    bcrypt = Bcrypt(app)
    login_manager = LoginManager(app)
    jwt = JWTManager(app)
    limiter = Limiter(app=app, key_func=lambda: '127.0.0.1')

    init_auth_module(app, app.mongo, login_manager, bcrypt, limiter)
    # Initialize books module 
    init_books_module(app, app.mongo, login_manager)

    yield app

@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


# Test get_books with authentication
def test_get_books_authenticated(client, mocker):
    # Mock the login_manager user loader
    mocker.patch('flask_login.utils._get_user', return_value=Mock(is_authenticated=True))
    
    response = client.get('/books/')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert 'books' in data

# Test add_book with valid data
def test_add_book_valid_data(client, mocker):
    # Mock the login_manager user loader
    mocker.patch('flask_login.utils._get_user', return_value=Mock(is_authenticated=True))

    # Define a valid book data
    valid_book_data = {
        'title': 'Test Book',
        'author': 'Test Author',
        'isbn': '1234567890'
    }

    response = client.post('/books/add', json=valid_book_data)
    assert response.status_code == 201
    data = json.loads(response.data.decode('utf-8'))
    assert 'message' in data
    assert 'book_id' in data

# Test get_books without authentication
def test_get_books_unauthenticated(client):
    response = client.get('/books/')
    assert response.status_code == 401

# Test add_book with invalid data
def test_add_book_invalid_data(client, mocker):
    # Mock the login_manager user loader
    mocker.patch('flask_login.utils._get_user', return_value=Mock(is_authenticated=True))

    # Define an invalid book data (missing required 'title' field)
    invalid_book_data = {
        'author': 'Test Author',
        'isbn': '1234567890'
    }

    response = client.post('/books/add', json=invalid_book_data)
    assert response.status_code == 400
    data = json.loads(response.data.decode('utf-8'))
    assert 'message' in data
    assert 'errors' in data

