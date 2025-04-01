import pymysql

# Paramètres de connexion (remplace par tes infos)
HOST = "sql7.freesqldatabase.com"  # Adresse du serveur MySQL
USER = "sql7770052"  # Ton identifiant MySQL
PASSWORD = "ilPzfpq7Vr"  # Ton mot de passe MySQL
DATABASE = "sql7770052"  # Nom de ta base de données

try:
    # Connexion à la base de données
    connection = pymysql.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    )
    
    # Si la connexion réussit
    print("✅ Connexion réussie à MySQL !")
    
    # Tester une requête SQL pour voir si la base est accessible
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print("📂 Tables disponibles :", tables)

except Exception as e:
    print(f"❌ Erreur de connexion MySQL : {e}")
