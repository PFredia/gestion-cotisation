from flask import Blueprint, render_template, request, jsonify
from extensions import db
from models.due import Due
from models.member import Member
from sqlalchemy import func
import datetime
from typing import List, Dict, Any, Union, Optional

reports = Blueprint('reports', __name__, url_prefix='/reports')

@reports.route('/')
def index():
    # Récupérer les statistiques de base
    # Use explicit column reference to avoid type checking issues
    total_dues = db.session.query(func.sum(Due.amount)).scalar() or 0
    total_members = Member.query.count()
    recent_dues = Due.query.order_by(Due.date.desc()).limit(5).all()
    
    # Calculer les statistiques par mois pour l'année en cours
    current_year = datetime.datetime.now().year
    
    # Use explicit column references for type checking
    monthly_stats = db.session.query(
        func.strftime('%m', Due.date).label('month'),
        func.sum(Due.amount).label('total')
    ).filter(
        func.strftime('%Y', Due.date) == str(current_year)
    ).group_by('month').all()
    
    # Formater les données pour le graphique
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    monthly_data = {month: 0.0 for month in months}  # type: Dict[str, float]
    
    # Handle potential None values from the database
    for stat in monthly_stats:
        if hasattr(stat, 'month') and hasattr(stat, 'total') and stat.month in monthly_data:
            monthly_data[stat.month] = float(stat.total) if stat.total is not None else 0.0
    
    chart_data = {
        'labels': ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc'],
        'data': list(monthly_data.values())
    }
    
    return render_template('reports/index.html', 
                          total_dues=total_dues,
                          total_members=total_members,
                          recent_dues=recent_dues,
                          chart_data=chart_data,
                          current_year=current_year)

@reports.route('/generate')
def generate_report():
    report_type = request.args.get('type', 'monthly')
    year = request.args.get('year', datetime.datetime.now().year)
    
    if report_type == 'monthly':
        # Générer rapport mensuel
        data = db.session.query(
            func.strftime('%m', Due.date).label('month'),
            func.sum(Due.amount).label('total')
        ).filter(
            func.strftime('%Y', Due.date) == str(year)
        ).group_by('month').all()
        
        result = [{'month': item.month, 'total': float(item.total)} for item in data]
        
    elif report_type == 'member':
        # Générer rapport par membre
        data = db.session.query(
            Member.id,
            Member.first_name,
            Member.last_name,
            func.sum(Due.amount).label('total')
        ).join(Due, Due.member_id == Member.id).filter(
            func.strftime('%Y', Due.date) == str(year)
        ).group_by(Member.id).all()
        
        result = [{'member_id': item.id, 
                  'name': f"{item.first_name} {item.last_name}", 
                  'total': float(item.total)} for item in data]
    
    return jsonify(result)