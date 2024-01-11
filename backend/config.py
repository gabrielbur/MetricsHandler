import os

class Config:
    MONGO_URI = os.getenv("MONGO_URI", 'mongodb://localhost:27017/booksdb')
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", 'your_jwt_secret_key')
    RATE_LIMIT_MONGO_URI = os.getenv("RATE_LIMIT_MONGO_URI", 'mongodb://localhost:27017/booksdb')
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_fallback_key')
    SESSION_TYPE = os.environ.get('SESSION_TYPE', 'filesystem')
