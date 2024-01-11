import pytest
from flask import Flask
from flask_socketio import SocketIO
from api.metrics import init_metrics_module
from flask_pymongo import PyMongo
from flask_login import LoginManager
from api.auth import init_auth_module
from datetime import datetime, timezone
from flask_limiter import Limiter
from flask_bcrypt import Bcrypt

# Flask app fixture
@pytest.fixture(scope='module')
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/testdb'

    app.mongo = PyMongo(app, uri=app.config['MONGO_URI'])
    socketio = SocketIO(app, cors_allowed_origins='*')
    bcrypt = Bcrypt(app)
    login_manager = LoginManager(app)
    limiter = Limiter(app=app, key_func=lambda: '127.0.0.1')
 
    
    init_auth_module(app, app.mongo, login_manager, bcrypt, limiter)
    init_metrics_module(app, app.mongo, socketio, login_manager)
    
    app.socketio = socketio

    yield app

@pytest.fixture
def client(app):
    # Use the SocketIO instance associated with the app for testing
    return app.socketio.test_client(app)

# Test for WebSocket connection
def test_websocket_connection(app, client):
    """ Test WebSocket connection. """
    client.connect()
    assert client.is_connected()
    client.disconnect()

# Test for requesting metrics via WebSocket
def test_request_metrics(app, client):
    """ Test requesting metrics via WebSocket. """
    with app.app_context():
        # Clear previous data and insert new test data
        app.mongo.db.metrics.delete_many({})
        for i in range(1, 6):
            app.mongo.db.metrics.insert_one({
                'name': 'test_metric',
                'value': i * 100,
                'timestamp': datetime(2021, 1, 1, i, 0, 0, tzinfo=timezone.utc)
            })

    client.connect()
    test_data = {
        'name': 'test_metric',
        'startDate': '2021-01-01T00:00:00Z',
        'endDate': '2021-01-02T00:00:00Z',
        'interval': 'hour',
        'include_zeros': False
    }

    print("Emitting request_metrics event...")
    client.emit('request_metrics', test_data)
    print("Waiting for response...")
    received = client.get_received()

    print("Received data:", received)
    assert received, "No data received from WebSocket"
    assert len(received[0]['args'][0]) > 0

    client.disconnect()



