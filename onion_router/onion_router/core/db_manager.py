import mariadb
import sys

class DBManager:
    """
    Gestionnaire de connexion et d'opérations sur la base de données MariaDB.
    """
    def __init__(self, host='127.0.0.1', user='root', password='password', database='onion_router'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conn = None

    def connect(self):
        """Établit la connexion à la base de données."""
        try:
            self.conn = mariadb.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                database=self.database
            )
            print(f"Connexion MariaDB réussie à {self.database}.")
        except mariadb.Error as e:
            print(f"Erreur de connexion MariaDB: {e}")
            sys.exit(1)

    def close(self):
        """Ferme la connexion à la base de données."""
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=None, fetch_mode='none'):
        """Exécute une requête SQL (SELECT, INSERT, UPDATE, DELETE)."""
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params)
            if fetch_mode == 'all':
                result = cursor.fetchall()
            elif fetch_mode == 'one':
                result = cursor.fetchone()
            else:
                result = None
            
            self.conn.commit()
            return result
            
        except mariadb.Error as e:
            print(f"Erreur lors de l'exécution de la requête: {e}")
            self.conn.rollback()
            return None
        finally:
            cursor.close()

    # =================================================================
    # Fonctions spécifiques à l'enregistrement des Routeurs
    # =================================================================

    def register_router(self, nom, ip, port, cle_publique, cle_privee):
        """Enregistre un nouveau routeur dans la table Routeurs."""
        query = """
        INSERT INTO Routeurs (Nom, Adresse_IP, Port, Cle_Publique, Cle_Privee)
        VALUES (?, ?, ?, ?, ?)
        ON DUPLICATE KEY UPDATE 
        Adresse_IP=VALUES(Adresse_IP), Port=VALUES(Port), Cle_Publique=VALUES(Cle_Publique), Cle_Privee=VALUES(Cle_Privee);
        """
        # Note: L'enregistrement de la clé privée ici est pour la démo/simplicité
        # Dans un vrai système, K_privee NE doit PAS être stockée par le Master.
        self.execute_query(query, (nom, ip, port, cle_publique, cle_privee))
        print(f"Routeur {nom} enregistré/mis à jour.")

    def get_all_router_keys(self):
        """Récupère tous les routeurs (IP, Port, Clé Publique) pour les clients."""
        query = "SELECT Nom, Adresse_IP, Port, Cle_Publique FROM Routeurs;"
        return self.execute_query(query, fetch_mode='all')