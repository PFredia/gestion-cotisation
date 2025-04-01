from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.member import Member
from models.user import User
from extensions import db
from werkzeug.security import generate_password_hash
from controllers.dashboard import treasurer_required
from datetime import datetime
import random
import string

# Création du blueprint pour les membres
members = Blueprint('members', __name__, url_prefix='/members')

# Function to generate a random password
def generate_password(length=8):
    """Generate a random password with the specified length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Function to create admin user
@members.route('/create_admin')
@login_required
@treasurer_required
def create_admin():
    # Check if admin already exists
    admin = User.query.filter_by(username='admin').first()
    if admin:
        flash('Admin user already exists!', 'warning')
        return redirect(url_for('members.index'))
    
    # Create admin user
    hashed_password = generate_password_hash('admin123', method='pbkdf2:sha256')
    
    admin = User()
    admin.username = 'admin'
    admin.email = 'admin@example.com'
    admin.password = hashed_password
    admin.role = 'admin'
    admin.created_at = datetime.utcnow()
    
    db.session.add(admin)
    db.session.commit()
    
    flash('Admin user created successfully! Username: admin, Password: admin123', 'success')
    return redirect(url_for('members.index'))

# Liste des membres
@members.route('/')
@login_required
@treasurer_required
def index():
    members_list = Member.query.all()
    return render_template('members/index.html', members=members_list)

# Ajouter un membre
@members.route('/add', methods=['GET', 'POST'])
@login_required
@treasurer_required
def add():
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        gender = request.form.get('gender')
        church_role = request.form.get('church_role')
        baptism_status = request.form.get('baptism_status')
        
        # Handle date fields properly
        date_of_birth_str = request.form.get('date_of_birth')
        date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date() if date_of_birth_str else None
        
        join_date_str = request.form.get('join_date')
        join_date = datetime.strptime(join_date_str, '%Y-%m-%d').date() if join_date_str else None
        
        profession = request.form.get('profession')
        notes = request.form.get('notes')
        
        # Create user account
        password = generate_password()
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        user = User()
        user.username = username
        user.email = email
        user.password = hashed_password
        user.role = 'member'
        user.created_at = datetime.utcnow()
        
        db.session.add(user)
        db.session.flush()  # To get the user ID
        
        # Create member
        member = Member()
        member.first_name = first_name
        member.last_name = last_name
        member.email = email
        member.phone = phone
        member.address = address
        member.gender = gender
        member.date_of_birth = date_of_birth
        member.profession = profession
        member.join_date = join_date
        member.church_role = church_role
        member.baptism_status = baptism_status
        member.notes = notes
        member.user_id = user.id
        member.created_at = datetime.utcnow()
        
        db.session.add(member)
        db.session.commit()
        
        flash(f'Membre ajouté avec succès! Nom d\'utilisateur: {username}, Mot de passe: {password}', 'success')
        return redirect(url_for('members.index'))
    
    return render_template('members/add.html')

@members.route('/edit/<int:member_id>', methods=['GET', 'POST'])
@login_required
@treasurer_required
def edit(member_id):
    member = Member.query.get_or_404(member_id)
    
    if request.method == 'POST':
        # Update member data
        member.first_name = request.form.get('first_name')
        member.last_name = request.form.get('last_name')
        member.email = request.form.get('email')
        member.phone = request.form.get('phone')
        member.address = request.form.get('address')
        member.gender = request.form.get('gender')
        member.church_role = request.form.get('church_role')
        member.baptism_status = request.form.get('baptism_status')
        member.profession = request.form.get('profession')
        member.notes = request.form.get('notes')
        
        # Handle date fields properly
        date_of_birth_str = request.form.get('date_of_birth')
        member.date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date() if date_of_birth_str else None
        
        join_date_str = request.form.get('join_date')
        member.join_date = datetime.strptime(join_date_str, '%Y-%m-%d').date() if join_date_str else None
        
        # Update user email if user exists
        if member.user:
            member.user.email = member.email
        
        db.session.commit()
        flash('Membre mis à jour avec succès!', 'success')
        return redirect(url_for('members.details', member_id=member.id))
    
    return render_template('members/edit.html', member=member)

# Détails d'un membre
@members.route('/<int:member_id>')
@login_required
@treasurer_required
def details(member_id):
    member = Member.query.get_or_404(member_id)
    return render_template('members/details.html', member=member)

# Supprimer un membre
@members.route('/delete/<int:member_id>')
@login_required
@treasurer_required
def delete(member_id):
    member = Member.query.get_or_404(member_id)
    
    # Supprimer également l'utilisateur associé
    if member.user:
        db.session.delete(member.user)
    
    db.session.delete(member)
    db.session.commit()
    
    flash('Membre supprimé avec succès!', 'success')
    return redirect(url_for('members.index'))