from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from extensions import db
from functools import wraps

# Create admin blueprint
admin = Blueprint('admin', __name__, url_prefix='/admin')

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Accès refusé. Vous devez être administrateur pour accéder à cette page.', 'danger')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin login
@admin.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in and is admin, redirect to admin dashboard
    if current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')  # Changed from username to email
        password = request.form.get('password') or ""  # Ensure password is a string
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()  # Changed from username to email
        
        # Check if user exists and is an admin
        if not user or not check_password_hash(user.password, password) or user.role != 'admin':
            flash('Identifiants invalides ou droits insuffisants.', 'danger')
            return redirect(url_for('admin.login'))
            
        # Log in the user
        login_user(user, remember=remember)
        session['is_admin'] = True
        
        flash('Connexion réussie!', 'success')
        return redirect(url_for('admin.dashboard'))
        
    return render_template('admin/login.html')

# Admin dashboard
@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get statistics for dashboard
    from models.member import Member
    from models.due import Due, DueType
    
    stats = {
        'total_members': Member.query.count(),
        'total_users': User.query.count(),
        'due_types': DueType.query.count(),
        'total_dues': sum([due.amount for due in Due.query.all()]) if Due.query.count() > 0 else 0
    }
    
    # Get recent dues and members
    recent_dues = Due.query.order_by(Due.id.desc()).limit(5).all()  # Using id instead of date
    recent_members = Member.query.order_by(Member.id.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                          stats=stats, 
                          recent_dues=recent_dues, 
                          recent_members=recent_members)

# Admin logout
@admin.route('/logout')
@login_required
@admin_required
def logout():
    logout_user()
    session.pop('is_admin', None)
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('admin.login'))


@admin.route('/users/<int:user_id>/reset-password', methods=['GET', 'POST'])
@login_required
@admin_required
def reset_user_password(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not new_password or not confirm_password:
            flash('Tous les champs sont requis', 'danger')
            return redirect(url_for('admin.reset_user_password', user_id=user.id))
            
        if new_password != confirm_password:
            flash('Les mots de passe ne correspondent pas', 'danger')
            return redirect(url_for('admin.reset_user_password', user_id=user.id))
            
        # Update password
        user.password = generate_password_hash(new_password)
        db.session.commit()
        
        flash(f'Le mot de passe de {user.username} a été réinitialisé avec succès', 'success')
        return redirect(url_for('admin.users'))
        
    return render_template('admin/reset_password.html', user=user)