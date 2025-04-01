import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'votre_clé_secrète'
    
    # Configuration de la base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///church_app.db'
    
    # Si l'URL commence par postgres://, la remplacer par postgresql://
    # (nécessaire pour SQLAlchemy avec PostgreSQL sur Render)
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False