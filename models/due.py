from extensions import db
from datetime import datetime

class DueType(db.Model):
    """Modèle pour les types de cotisations"""
    __tablename__ = 'due_type'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    # Add this line:
    suggested_amount = db.Column(db.Float, nullable=True)
    description = db.Column(db.Text, nullable=True)
    frequency = db.Column(db.String(20), default='monthly')  # monthly, quarterly, yearly
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relations
    dues = db.relationship('Due', backref='due_type', lazy=True)
    
    def __repr__(self):
        return f"<DueType {self.name}>"

# Add the total_amount field to your Due model
class Due(db.Model):
    __tablename__ = 'due'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    due_type_id = db.Column(db.Integer, db.ForeignKey('due_type.id'))
    amount_paid = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=True, default=0)  # Add this line
    payment_date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.String(50), default='cash')
    notes = db.Column(db.Text, nullable=True)
    recorded_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f"<Due {self.id} - {self.amount_paid}>"