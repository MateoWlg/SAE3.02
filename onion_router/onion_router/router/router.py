import socket
import threading
import json
import time
import random
import sys

# Importation des configurations et des modules
sys.path.append('.') 
sys.path.append('core')
from config import MASTER_IP, MASTER_PORT, DB_CONFIG
from crypto_simple import generate_keys, decrypt_data, text_to_int, int_to_text
from db_manager import DBManager

class Router:
    
    # ... (le code des méthodes Router.__init__, register_with_master, 
    # handle_message, et send_to_next_hop est le même que précédemment)
    
    def __init__(self, name, listen_ip, port): # listen_ip est l'IP de la VM du Routeur
        self.name = name
        self.ip = listen_ip
        self.port = port
        self.private_key, self.public_key, self.n_module = generate_keys()
        self.db = DBManager(**DB_CONFIG)
        # ... (suite de l'initialisation inchangée)
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.ip, self.port)) # Liaison sur l'IP spécifique de la VM
        self.server_socket.listen(5)
        print(f"Routeur {self.name} démarré. Clé Publique: {self.public_key}")

    def register_with_master(self):
        # ... (Utilise MASTER_IP et MASTER_PORT du fichier config)
        pass

    def handle_message(self, conn, addr):
        # ... (Logique de déchiffrement et routage inchangée)
        pass

    def send_to_next_hop(self, ip, port, payload):
        # ... (Logique d'envoi inchangée)
        pass

    def start_listening(self):
        # ... (Logique d'écoute multithread inchangée)
        pass

if __name__ == '__main__':
    try:
        router_name = sys.argv[1]
        router_port = int(sys.argv[2])
        router_listen_ip = sys.argv[3] # NOUVEAU: l'IP d'écoute de ce routeur
    except IndexError:
        print("Usage: python router.py <nom_routeur> <port_ecoute> <ip_ecoute>")
        sys.exit(1)
        
    router = Router(router_name, router_listen_ip, router_port)
    router.register_with_master()
    router.start_listening()