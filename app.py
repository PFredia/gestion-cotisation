import os
from dotenv import load_dotenv
from flask import Flask, redirect, url_for
from config import Config
from extensions import db, login_manager  # Keep this import
from flask_migrate import Migrate
# Remove this import: from flask_sqlalchemy import SQLAlchemy

# Chemin absolu du répertoire du projet
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Charger les variables d'environnement depuis .env
# Utiliser un chemin absolu pour charger le fichier .env
dotenv_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path)

# Remove this line: db = SQLAlchemy()

# Create app
def create_app():
    # Configurer le dossier statique et templates avec des chemins absolus
    app = Flask(__name__, 
                static_folder=os.path.join(BASE_DIR, 'static'),
                template_folder=os.path.join(BASE_DIR, 'templates'))
    
    # Mettre à jour la configuration avec le chemin de base
    app.config.from_object(Config)
    app.config['BASE_DIR'] = BASE_DIR

    # Chemins absolus pour les imports de modules
    import sys
    sys.path.insert(0, BASE_DIR)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # type: ignore
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    # Import models
    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Import and register blueprints
    from controllers.auth import auth
    from controllers.dashboard import dashboard
    from controllers.members import members
    from controllers.dues import dues
    from controllers.users import users
    from controllers.reports import reports  # Ajouter cette ligne

    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(members)
    app.register_blueprint(dues)
    app.register_blueprint(users)
    app.register_blueprint(reports)  # Ajouter cette ligne

    # Add favicon route to prevent 404 errors
    @app.route('/favicon.ico')
    def favicon():
        return app.send_static_file('favicon.ico')

    return app, migrate  # Return migrate along with app

# Create the app instance
app, migrate = create_app()  # Get both app and migrate

# Add a basic route for the root URL
@app.route('/')
def index():
    return redirect(url_for('auth.login'))

# Add a route for register page
@app.route('/register')
def register_redirect():
    return redirect(url_for('auth.register'))


@app.route('/undefined-variable')
def undefined_variable():
    # Using Flask's abort to properly handle errors
    from flask import abort
    # This will raise a 500 Internal Server Error
    abort(500, description="This route intentionally raises an error")
    # The line below is unreachable but kept for reference
    # return my_undefined_variable  # Cette variable n'existe pas

# Import traceback module
import traceback

@app.errorhandler(Exception)
def handle_exception(e):
    print("❌ ERREUR DÉTECTÉE :", traceback.format_exc())  # Affiche l'erreur complète dans la console
    return "Erreur interne du serveur", 500





if __name__ == "__main__":
    # Ajoutez ces imports en haut de votre fichier
    import logging
    from logging.handlers import RotatingFileHandler
    import os
    
    # À la fin de votre fichier, avant de lancer l'application
    if __name__ == '__main__':
        # Assurez-vous que le dossier logs existe
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Configuration du logger
        file_handler = RotatingFileHandler('logs/church_app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Church Management App startup')
        
        # Create database tables
        with app.app_context():
            db.create_all()
        
        # Run the app - use only one app.run() call
        app.run(host='0.0.0.0', debug=True)