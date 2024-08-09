from data.extensions import db
from uuid import uuid4
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id: Mapped[str] = mapped_column(primary_key=True, default = str(uuid4()))
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
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
    
    # Db instance methods
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def save(self):
        db.session.add(self)
        db.session.commit()