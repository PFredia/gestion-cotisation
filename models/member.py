from extensions import db
from datetime import datetime

class Member(db.Model):
    __tablename__ = 'member'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    # Modification du champ gender pour mieux représenter le genre
    gender = db.Column(db.String(10), nullable=True)  # 'Masculin' ou 'Féminin'
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    profession = db.Column(db.String(100), nullable=True)
    join_date = db.Column(db.Date, nullable=True)
    church_role = db.Column(db.String(50), nullable=True)
    baptism_status = db.Column(db.String(20), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Member {self.first_name} {self.last_name}>"