import socket
import threading
import json
import time
import sys

# Importation des configurations et des modules
sys.path.append('.') # Permet d'importer config.py
sys.path.append('core')
from config import MASTER_IP, MASTER_PORT, DB_CONFIG
from db_manager import DBManager
from crypto_simple import N_MODULE

# (Le reste du code de la classe MasterServer et de ses méthodes handle_connection, 
# register_router_info, et send_router_keys est identique à la proposition précédente)

class MasterServer:
    # ... (le code des méthodes MasterServer.__init__, handle_connection, 
    # register_router_info, send_router_keys, et start est le même que précédemment)
    
    def __init__(self):
        self.db = DBManager(**DB_CONFIG)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((MASTER_IP, MASTER_PORT))
        self.server_socket.listen(5)
        print(f"Master démarré. Écoute sur {MASTER_IP}:{MASTER_PORT}...")
        self.db.connect()
        
    def handle_connection(self, conn, addr):
        # ... (code inchangé)
        pass

    def register_router_info(self, conn, message):
        # ... (code inchangé)
        pass

    def send_router_keys(self, conn):
        # ... (code inchangé)
        pass

    def start(self):
        # ... (code inchangé)
        pass

if __name__ == '__main__':
    # Initialisation de la BDD et création de la table 
    db_init = DBManager(**DB_CONFIG)
    db_init.connect()
    # (Exécution du script CREATE TABLE pour s'assurer qu'elle existe)
    db_init.execute_query("""
    CREATE TABLE IF NOT EXISTS Routeurs (
        RouterID INT PRIMARY KEY AUTO_INCREMENT,
        Nom VARCHAR(50) NOT NULL UNIQUE,
        Adresse_IP VARCHAR(15) NOT NULL,
        Port INT NOT NULL,
        Cle_Publique INT NOT NULL, 
        Cle_Privee INT NOT NULL 
    );
    """)
    db_init.close()
    
    server = MasterServer()
    server.start()