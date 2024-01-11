from flask_login import UserMixin
from pydantic import BaseModel

class User(UserMixin):
    def __init__(self, user_data):
        self.user_data = user_data

    def get_id(self):
        return str(self.user_data['_id'])


class LoginRequest(BaseModel):
    username: str
    password: str