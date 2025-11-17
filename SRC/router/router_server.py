import socket
import threading
import json
from crypto.rsa_custom import RSACustom

class RouterServer:
    def __init__(self, router_id, host='localhost', port=6000):
        self.router_id = router_id
        self.host = host
        self.port = port
        self.crypto = RSACustom()
        self.private_key, self.public_key = self.crypto.generate_keys()
        
    def start(self):
        # S'enregistrer auprès du master
        self.register_with_master()
        
        # Démarrer le serveur
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Router {self.router_id} listening on {self.host}:{self.port}")
        
        while True:
            client_socket, address = server_socket.accept()
            threading.Thread(target=self.handle_message, args=(client_socket,)).start()
    
    def register_with_master(self):
        try:
            master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            master_socket.connect(('localhost', 5000))
            
            registration = {
                'type': 'router_register',
                'router_id': self.router_id,
                'host': self.host,
                'port': self.port,
                'public_key': self.public_key
            }
            master_socket.send(json.dumps(registration).encode())
            response = master_socket.recv(1024).decode()
            print(f"Registration response: {response}")
            master_socket.close()
            
        except Exception as e:
            print(f"Failed to register with master: {e}")
    
    def handle_message(self, client_socket):
        try:
            data = client_socket.recv(4096).decode()
            message = json.loads(data)
            
            if message['type'] == 'onion_message':
                self.process_onion_message(message, client_socket)
                
        except Exception as e:
            print(f"Router {self.router_id} error: {e}")
        finally:
            client_socket.close()
    
    def process_onion_message(self, message, socket):
        encrypted_layer = message['encrypted_layer']
        
        # Déchiffrer la couche avec la clé privée
        decrypted_data = self.crypto.decrypt(encrypted_layer, self.private_key)
        next_hop_info = json.loads(decrypted_data)
        
        print(f"Router {self.router_id} decrypted: {next_hop_info}")
        
        if 'next_hop' in next_hop_info:
            # Transmettre au prochain routeur
            self.forward_to_next_hop(next_hop_info)
        else:
            # Message final pour le client destinataire
            self.deliver_to_client(next_hop_info)
    
    def forward_to_next_hop(self, next_hop_info):
        try:
            next_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            next_socket.connect((next_hop_info['next_hop']['host'], 
                               next_hop_info['next_hop']['port']))
            
            forward_message = {
                'type': 'onion_message',
                'encrypted_layer': next_hop_info['remaining_message']
            }
            next_socket.send(json.dumps(forward_message).encode())
            next_socket.close()
            
        except Exception as e:
            print(f"Forwarding error: {e}")