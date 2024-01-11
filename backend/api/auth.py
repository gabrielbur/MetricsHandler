from flask import Blueprint, request, jsonify, abort
from flask_login import login_user, logout_user, login_required
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_limiter import Limiter
from loguru import logger
from typing import Tuple, Dict, Optional
from http import HTTPStatus
from datetime import timedelta
from models import User, LoginRequest



def init_auth_module(app, mongo, login_manager, _bcrypt, limiter: Limiter):
    auth_bp = Blueprint('auth', __name__)

    
    @login_manager.user_loader
    def load_user(user_id: str) -> Optional[User]:
        user_data = mongo.db.users.find_one({'_id': int(user_id)})
        return User(user_data) if user_data else None

    @login_manager.unauthorized_handler
    def unauthorized():
        logger.warning(f"Unauthorized request - Method: {request.method}, URL: {request.url}")
        abort(HTTPStatus.UNAUTHORIZED)

    @auth_bp.route('/login', methods=['POST'])
    @limiter.limit("10 per minute")
    def login() -> Tuple[Dict, int]:
        try:
            req = LoginRequest(**request.get_json())
        except ValueError as e:
            abort(HTTPStatus.BAD_REQUEST)

        user_data = mongo.db.users.find_one({'username': req.username})
        if user_data and _bcrypt.check_password_hash(user_data['password'], req.password.encode('utf-8')):
            user = User(user_data)
            login_user(user, remember=True)
            access_token = create_access_token(identity=str(user_data['_id']), expires_delta=timedelta(hours=1))
            logger.info(f"User {req.username} logged in")
            return jsonify({'message': 'Login successful', 'token': access_token}), HTTPStatus.OK
        else:
            return jsonify({'message': 'Login failed'}), HTTPStatus.UNAUTHORIZED

    @auth_bp.route('/logout')
    @login_required
    @limiter.limit("10 per minute")
    def logout() -> Tuple[Dict, int]:
        logout_user()
        return jsonify({'message': 'Logout successful'}), HTTPStatus.OK

    @auth_bp.route('/validate_token', methods=['POST'])
    @jwt_required()
    @limiter.limit("5 per minute")
    def validate_token() -> Tuple[Dict, int]:
        try:
            current_user_id = get_jwt_identity()
            user_data = mongo.db.users.find_one({'_id': int(current_user_id)})

            if user_data:
                return jsonify({'valid': True}), HTTPStatus.OK
            else:
                return jsonify({'valid': False, 'message': 'User not found'}), HTTPStatus.UNAUTHORIZED
        except Exception as e:
            logger.error(f'Token validation error: {str(e)}')
            abort(HTTPStatus.INTERNAL_SERVER_ERROR)
            
    app.register_blueprint(auth_bp)
