from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_pymongo import PyMongo
from loguru import logger
import config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config.Config)
app.secret_key = 'test_jwt_secret_key'

    
# Initialize Flask extensions
CORS(app, supports_credentials=True, resources={r"/*": {
    "origins": "*",  # Adjust this in production
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Origin", "Content-Type", "X-Auth-Token", "Authorization"]
}})


mongo = PyMongo(app)
jwt = JWTManager(app)
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)  
limiter = Limiter(app=app, key_func=get_remote_address)
socketio = SocketIO(app, cors_allowed_origins='*')
# Import and initialize modules
from api.auth import init_auth_module
from api.metrics import init_metrics_module
from api.books import init_books_module

init_auth_module(app, mongo, login_manager, bcrypt, limiter)
init_metrics_module(app, mongo, socketio, login_manager)
init_books_module(app, mongo, login_manager)

logger.add("logs/app.log", rotation="500 MB", level="ERROR")

if __name__ == '__main__':
    socketio.run(app, debug=True)
