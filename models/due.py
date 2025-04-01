from extensions import db
from datetime import datetime
from sqlalchemy.orm import relationship
from typing import Optional, Any

class Due(db.Model):
    __tablename__ = 'dues'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)  # Make sure this field exists
    date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(255))
    
    # Define relationship
    member = relationship('Member', back_populates='dues')
    
    def __repr__(self) -> str:
        return f'<Due {self.id}: {self.amount}>'