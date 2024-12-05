import os
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, NoResultFound

from app.main.model.user import User

class UserService:

    def __init__(self, db: SQLAlchemy):
        self.db: SQLAlchemy = db

    def create_user(self, username, password):
        user = User(username, password)

        try:
            with current_app.app_context():
                try:
                    user_dir = os.path.join(current_app.config['data_dir'], username)
                    os.makedirs(user_dir)
                except FileExistsError as e:
                    raise e
            self.db.session.begin()
            self.db.session.add(user)
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            raise e

        return user

    def get_token(self, username, password):
        try:
            user = User.query.filter_by(username=username).one()
            token = user.get_token(password)
            if not token:
                print("Invalid password")
            return token
        except NoResultFound:
            print("NoResultFound")
            return None

    def find_by_token(self, token):
        return self.db.session.query(User).filter_by(access_token=token).first()

    def delete_user(self, token):
        try:
            User.query.filter_by(access_token=token).delete()
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            raise e
