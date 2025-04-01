import os
from dotenv import load_dotenv

# Chemin absolu du répertoire du projet
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Chemin absolu du fichier .env
DOTENV_PATH = os.path.join(BASE_DIR, '.env')

# Charger les variables d'environnement depuis .env avec un chemin absolu
load_dotenv(DOTENV_PATH)

class Config:
    # Clé secrète
    SECRET_KEY = os.getenv("SECRET_KEY", "une_clé_secrète_par_défaut")
    
    # Chemin de base de données portable
    DATABASE_PATH = os.path.join(BASE_DIR, 'church.db')
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH}")


    print("🔍 DATABASE_URL chargé depuis .env :", os.getenv("DATABASE_URL"))
    print("🔍 SQLALCHEMY_DATABASE_URI utilisée :", SQLALCHEMY_DATABASE_URI)

    
    # Autres configurations
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Chemin de base du projet
    BASE_DIR = BASE_DIR