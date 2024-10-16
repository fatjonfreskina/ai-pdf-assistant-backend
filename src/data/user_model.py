from data.extensions import db
from uuid import uuid4
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    password: Mapped[str]
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password: str) -> None:
        self.password = generate_password_hash(password)
        
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)
    
    @classmethod
    def get_user_by_username(cls, username: str) -> 'User':
        return cls.query.filter_by(username=username).first()

    @classmethod
    def validate_password(cls, new_password: str) -> bool:
        # If needed, implement additional checking here, although most of it will be done in the frontend.
        return True

    @classmethod
    def get_user_by_email(cls, email: str) -> 'User':
        return cls.query.filter_by(email=email).first()
    
    # Db instance methods
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def save(self):
        db.session.add(self)
        db.session.commit()