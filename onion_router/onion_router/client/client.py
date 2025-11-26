import socket
import json
import random
import sys
import threading

# Importation des configurations et des modules
sys.path.append('.') 
sys.path.append('core')
from config import MASTER_IP, MASTER_PORT, CLIENT_A_IP, CLIENT_A_PORT, CLIENT_B_IP, CLIENT_B_PORT
from crypto_simple import encrypt_data, text_to_int, int_to_text

class OnionClient:
    
    # ... (Le code des méthodes OnionClient.get_router_info, build_onion, 
    # send_message, handle_incoming_message, et start_listener est le même que précédemment)
    
    def __init__(self, name, listen_ip, listen_port): # NOUVEAU: Ajout de listen_ip
        self.name = name
        self.ip = listen_ip
        self.port = listen_port
        self.router_data = [] 
        print(f"Client {self.name} démarré. Écoute sur {self.ip}:{self.port} pour le message final.")
        
    def get_router_info(self):
        # Utilise MASTER_IP et MASTER_PORT du fichier config
        pass

    # ... (autres méthodes inchangées)

if __name__ == '__main__':
    # Le Master et les Routeurs doivent être démarrés en premier.
    # Ex: R1(8001) sur VM2, R2(8002) sur VM2, R3(8003) sur VM3

    try:
        client_name = sys.argv[1]
    except IndexError:
        print("Usage: python client.py <nom_client> (ex: ClientA ou ClientB)")
        sys.exit(1)

    if client_name == "ClientA":
        client_a = OnionClient("Client A", CLIENT_A_IP, CLIENT_A_PORT)
        
        # Démarrage de l'écoute
        listener_thread = threading.Thread(target=client_a.start_listener)
        listener_thread.daemon = True
        listener_thread.start()

        time.sleep(2) 
        
        if client_a.get_router_info():
            # Destinataire: Client B (qui doit être démarré sur son propre terminal)
            client_b_addr = f"{CLIENT_B_IP}:{CLIENT_B_PORT}"
            message = f"Bonjour Client B, de la part de {client_name}. (Test à {time.strftime('%H:%M:%S')})"
            client_a.send_message("Client B", client_b_addr, message)

    elif client_name == "ClientB":
        # Client B s'initialise et écoute simplement
        client_b = OnionClient("Client B", CLIENT_B_IP, CLIENT_B_PORT)
        client_b.start_listener()
        
    else:
        print("Nom de client inconnu. Utilisez ClientA ou ClientB.")