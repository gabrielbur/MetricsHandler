from unittest.mock import Mock
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask import Flask, json
from flask_login import LoginManager
from flask_socketio import SocketIO
import pytest
from api.metrics import init_metrics_module
from flask.testing import FlaskClient
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from api.auth import init_auth_module
from datetime import datetime, timezone

# Fixture for Flask app
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
    socketio = SocketIO(app, cors_allowed_origins='*')

    init_auth_module(app, app.mongo, login_manager, bcrypt, limiter)
    init_metrics_module(app, app.mongo, socketio, login_manager)

    yield app

@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client

# Mock user loader for Flask-Login
class MockUser:
    def __init__(self, user_id='testuser', is_authenticated=True):
        self.id = user_id
        self.is_authenticated = is_authenticated

# Test logging metrics
def test_log_metrics(client, mocker):
    mocker.patch('flask_login.utils._get_user', return_value=MockUser())

    metric_data = {
        'name': 'test_metric',
        'value': 123
    }

    response = client.post('/metrics/log_metrics', json=metric_data)
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == 'Metric logged successfully'

# Test retrieving metrics
def test_get_metrics(client, mocker):
    mocker.patch('flask_login.utils._get_user', return_value=MockUser())

    start_date = datetime.now(timezone.utc).isoformat()
    end_date = datetime.now(timezone.utc).isoformat()

    metrics_request = {
        'name': 'test_metric',
        'startDate': start_date,
        'endDate': end_date,
        'interval': 'hour',
        'include_zeros': False
    }

    response = client.post('/metrics/get_metrics', json=metrics_request)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'metrics' in data
    assert isinstance(data['metrics'], list)

