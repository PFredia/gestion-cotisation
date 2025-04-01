from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from extensions import db  # Import from extensions instead of app

# Création du blueprint pour l'authentification
auth = Blueprint('auth', __name__, url_prefix='/auth')

# Route pour l'inscription
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password') or ""  # Provide default empty string if None

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Cet email est déjà utilisé.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Create user with all required fields
        new_user = User()  # Create empty user object
        new_user.username = username
        new_user.email = email
        new_user.password = generate_password_hash(password)
        new_user.role = 'member'  # Default role
        
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        flash('Inscription réussie !', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('auth/register.html')

# Route pour la connexion
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Validate form data
        if not username or not password:
            flash('Veuillez remplir tous les champs', 'danger')
            return redirect(url_for('auth.login'))
        
        print(f"Tentative de connexion avec username: {username}")
        
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"Utilisateur avec username {username} non trouvé dans la base de données")
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Try to verify password
        try:
            password_matches = check_password_hash(user.password, password)
            
            if password_matches:
                login_user(user)
                flash('Connexion réussie !', 'success')
                return redirect(url_for('dashboard.index'))
            else:
                flash('Nom d\'utilisateur ou mot de passe incorrect.', 'danger')
                return redirect(url_for('auth.login'))
        except Exception as e:
            print(f"Erreur lors de la vérification du mot de passe: {str(e)}")
            flash('Erreur lors de la connexion.', 'danger')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/login.html')

# Route pour la déconnexion
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Déconnexion réussie.', 'success')
    return redirect(url_for('auth.login'))

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if not current_password or not new_password or not confirm_password:
            flash('Tous les champs sont requis', 'danger')
            return redirect(url_for('auth.change_password'))
            
        if new_password != confirm_password:
            flash('Les nouveaux mots de passe ne correspondent pas', 'danger')
            return redirect(url_for('auth.change_password'))
            
        # Check current password
        if not check_password_hash(current_user.password, current_password):
            flash('Mot de passe actuel incorrect', 'danger')
            return redirect(url_for('auth.change_password'))
            
        # Update password
        current_user.password = generate_password_hash(new_password)
        db.session.commit()
        
        flash('Votre mot de passe a été mis à jour avec succès', 'success')
        return redirect(url_for('dashboard.index'))
        
    return render_template('auth/change_password.html')
