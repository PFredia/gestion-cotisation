from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.user import User
from extensions import db
from werkzeug.security import generate_password_hash
from controllers.dashboard import admin_required, treasurer_required

# Création du blueprint pour les utilisateurs
users = Blueprint('users', __name__, url_prefix='/users')

# Liste des utilisateurs
@users.route('/')
@login_required
@admin_required
def index():
    users_list = User.query.all()
    return render_template('users/index.html', users=users_list)

# Ajouter un utilisateur
@users.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password') or ""  # Ensure password is a string
        role = request.form.get('role') or "member"  # Ensure role is a string with default value
        
        # Vérifier si l'utilisateur existe déjà
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Ce nom d\'utilisateur est déjà utilisé.', 'danger')
            return redirect(url_for('users.add'))
        
        # Créer l'utilisateur
        new_user = User()
        new_user.username = username
        new_user.email = email
        new_user.password = generate_password_hash(password)
        new_user.role = role
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Utilisateur ajouté avec succès!', 'success')
        return redirect(url_for('users.index'))
    
    return render_template('users/add.html')

# Modifier un utilisateur
@users.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@treasurer_required
def edit(user_id):
    utilisateur = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        utilisateur.username = request.form.get('username')
        utilisateur.email = request.form.get('email')
        utilisateur.role = request.form.get('role') or "member"  # Ensure role is a string with default value
        
        # Mettre à jour le mot de passe si fourni
        password = request.form.get('password')
        if password and password.strip():  # Check if password exists and is not empty
            utilisateur.password = generate_password_hash(password)
        
        db.session.commit()
        flash('Utilisateur modifié avec succès!', 'success')
        return redirect(url_for('users.index'))
    
    return render_template('users/edit.html', utilisateur=utilisateur)

# Supprimer un utilisateur
@users.route('/delete/<int:user_id>')
@login_required
@admin_required
def delete(user_id):
    # Ne pas permettre de supprimer son propre compte
    if user_id == current_user.id:
        flash('Vous ne pouvez pas supprimer votre propre compte.', 'danger')
        return redirect(url_for('users.index'))
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    flash('Utilisateur supprimé avec succès!', 'success')
    return redirect(url_for('users.index'))