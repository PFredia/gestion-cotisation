from extensions import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'user'  # Changé de 'users' à 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='member')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with Member
    member = db.relationship('Member', backref='user', uselist=False, cascade="all, delete-orphan")