import socket
import threading
import json
from crypto.rsa_custom import RSACustom

class ClientApp:
    def __init__(self, client_id):
        self.client_id = client_id
        self.crypto = RSACustom()
        self.public_keys = {}  # Clés des routeurs
        self.master_host = 'localhost'
        self.master_port = 5000
        
    def fetch_public_keys(self):
        try:
            master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            master_socket.connect((self.master_host, self.master_port))
            
            request = {'type': 'client_key_request'}
            master_socket.send(json.dumps(request).encode())
            response = master_socket.recv(4096).decode()
            keys_data = json.loads(response)
            
            self.public_keys = keys_data['routers']
            master_socket.close()
            print("Public keys fetched successfully")
            
        except Exception as e:
            print(f"Failed to fetch public keys: {e}")
    
    def send_message(self, destination, message, route_chain):
        if not self.public_keys:
            self.fetch_public_keys()
        
        # Construction de l'oignon (de la fin vers le début)
        current_payload = json.dumps({
            'destination': destination,
            'message': message
        })
        
        # Chiffrement en couches inverses
        for router_id in reversed(route_chain):
            router_info = self.public_keys[router_id]
            next_hop = self.get_next_hop(router_id, route_chain)
            
            layer_data = {
                'next_hop': next_hop,
                'remaining_message': current_payload
            }
            
            # Chiffrer avec la clé publique du routeur
            current_payload = self.crypto.encrypt(
                json.dumps(layer_data), 
                router_info['public_key']
            )
        
        # Envoyer au premier routeur
        first_router = route_chain[0]
        first_router_info = self.public_keys[first_router]
        
        try:
            router_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            router_socket.connect((first_router_info['host'], first_router_info['port']))
            
            onion_message = {
                'type': 'onion_message',
                'encrypted_layer': current_payload
            }
            router_socket.send(json.dumps(onion_message).encode())
            router_socket.close()
            print("Message sent through onion routing")
            
        except Exception as e:
            print(f"Failed to send message: {e}")
    
    def get_next_hop(self, current_router, route_chain):
        current_index = route_chain.index(current_router)
        if current_index + 1 < len(route_chain):
            next_router = route_chain[current_index + 1]
            return self.public_keys[next_router]
        else:
            return None  # Dernier saut vers le client