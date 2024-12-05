import bcrypt
from app.main.extensions import db
import os
import base64

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    _password_hash = db.Column(db.String(255), nullable=False)
    access_token = db.Column(db.String(255), nullable=False, unique=True)

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)
        self.generate_access_token()

    def set_password(self, password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        self._password_hash = base64.b64encode(hashed_password).decode('utf-8')

    def get_token(self, password):
        hashed_password = base64.b64decode(self._password_hash.encode('utf-8'))
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            return self.access_token
        return None

    def generate_access_token(self):
        raw_token = os.urandom(32)
        self.access_token = base64.b64encode(raw_token).decode('utf-8')

    def __repr__(self):
        return f"<User {self.username}>"

