import pytest
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from mongomock import MongoClient
from api.auth import init_auth_module
from datetime import datetime, timezone

# Flask app setup for testing
app = Flask(__name__)
app.config['TESTING'] = True
app.config['JWT_SECRET_KEY'] = 'test_jwt_secret_key'
app.secret_key = 'test_jwt_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
jwt = JWTManager(app)
limiter = Limiter(app=app, key_func=lambda: '127.0.0.1')

# Fixture for mocked database
@pytest.fixture(scope="module")
def mock_db():
    mongo = MongoClient()
    _db = mongo.db
    yield mongo
    mongo.drop_database(_db)

# Fixture for initializing the auth module with the mock database
@pytest.fixture(scope="module")
def init_auth(mock_db):
    init_auth_module(app, mock_db, login_manager, bcrypt, limiter)

@pytest.fixture
def client(init_auth, mock_db):
    with app.test_client() as client:
        yield client

@pytest.fixture
def example_user(mock_db):
    mock_db.db.users.delete_many({}) 
    user_data = {
        '_id': 1,
        'username': 'testuser',
        'password': bcrypt.generate_password_hash('password').decode('utf-8'),
        'created': datetime.now(timezone.utc),
        'lastUpdated': datetime.now(timezone.utc),
    }
    mock_db.db.users.insert_one(user_data)
    return user_data

def test_login_success(client, example_user):
    response = client.post('/login', json={
        'username': example_user['username'],
        'password': 'password'
    })
    assert response.status_code == 200
    assert 'token' in response.json

def test_login_failure(client):
    response = client.post('/login', json={
        'username': 'nonexistent',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401

def test_logout(client, example_user):
    # Mock login
    response = client.post('/login', json={
        'username': example_user['username'],
        'password': 'password'
    })
    assert response.status_code == 200

    response = client.get('/logout')
    assert response.status_code == 200

def test_validate_token(client, example_user):
    # Mock login
    response = client.post('/login', json={
        'username': example_user['username'],
        'password': 'password'
    })
    assert response.status_code == 200
    token = response.json.get('token')

    response = client.post('/validate_token', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200

if __name__ == '__main__':
    pytest.main()
