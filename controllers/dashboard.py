from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.user import User
from models.member import Member
from models.due import Due, DueType  # DueType is already imported here
from extensions import db
from functools import wraps

# Remove the duplicate imports
# from models.member import Member
# from models.due_type import DueType  <- This is causing the error

# Création du blueprint pour le tableau de bord
dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')

# Décorateur pour vérifier si l'utilisateur est un administrateur
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Accès refusé. Vous devez être administrateur.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

# Décorateur pour vérifier si l'utilisateur est un trésorier ou un administrateur
def treasurer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role not in ['treasurer', 'admin']:
            flash('Accès refusé. Vous devez être trésorier ou administrateur.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

# Route principale du tableau de bord
@dashboard.route('/')
@login_required
def index():
    # Rediriger vers le tableau de bord approprié en fonction du rôle
    if current_user.role == 'admin':
        return redirect(url_for('dashboard.admin'))
    elif current_user.role == 'treasurer':
        return redirect(url_for('dashboard.treasurer'))
    else:
        return redirect(url_for('dashboard.member'))

# Tableau de bord administrateur
@dashboard.route('/admin')
@login_required
@admin_required
def admin():
    from models.member import Member
    from models.due import Due, DueType
    from models.user import User
    
    # Create stats dictionary to match what the template expects
    stats = {
        'total_members': Member.query.count(),
        'total_users': User.query.count(),
        'due_types': DueType.query.count(),
        'total_dues': sum([due.amount_paid for due in Due.query.all()]) if Due.query.count() > 0 else 0
    }
    
    # Get recent dues and members for the dashboard
    recent_dues = Due.query.order_by(Due.id.desc()).limit(5).all()
    recent_members = Member.query.order_by(Member.id.desc()).limit(5).all()
    
    # Create dictionaries for efficient lookups
    member_ids = [due.member_id for due in recent_dues if due.member_id]
    due_type_ids = [due.due_type_id for due in recent_dues if due.due_type_id]
    user_ids = [due.recorded_by for due in recent_dues if due.recorded_by]
    
    member_dict = {m.id: m for m in Member.query.filter(Member.id.in_(member_ids)).all()} if member_ids else {}
    due_type_dict = {dt.id: dt for dt in DueType.query.filter(DueType.id.in_(due_type_ids)).all()} if due_type_ids else {}
    user_dict = {u.id: u for u in User.query.filter(User.id.in_(user_ids)).all()} if user_ids else {}
    
    return render_template('admin/dashboard.html', 
                          stats=stats, 
                          recent_dues=recent_dues, 
                          recent_members=recent_members,
                          member_dict=member_dict,
                          due_type_dict=due_type_dict,
                          user_dict=user_dict)

# Tableau de bord trésorier
@dashboard.route('/treasurer')
@login_required
@treasurer_required
def treasurer():
    # Get all members
    members = Member.query.all()
    
    # Get recent dues
    recent_dues = Due.query.order_by(Due.payment_date.desc()).limit(5).all()
    
    # Create member and due type dictionaries for easy lookup
    member_dict = {member.id: member for member in Member.query.all()}
    due_type_dict = {due_type.id: due_type for due_type in DueType.query.all()}
    
    return render_template('dashboard/treasurer.html', 
                          members=members, 
                          recent_dues=recent_dues,
                          member_dict=member_dict,
                          due_type_dict=due_type_dict)

# Tableau de bord membre
@dashboard.route('/member')
@login_required
def member():
    # Vérifier si l'utilisateur a un profil de membre associé
    member = None
    if current_user.member:
        member = current_user.member
        dues = Due.query.filter_by(member_id=member.id).order_by(Due.payment_date.desc()).all()
    else:
        dues = []
    
    return render_template('dashboard/member.html', member=member, dues=dues)

# Add these helper functions
# Fix the template filter functions - they should be registered to the blueprint
@dashboard.app_template_filter('get_member')
def get_member(member_id):
    return Member.query.get(member_id)

@dashboard.app_template_filter('get_due_type')
def get_due_type(due_type_id):
    return DueType.query.get(due_type_id)