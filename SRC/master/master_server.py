import socket
import threading
import json
from database.db_manager import DatabaseManager

class MasterServer:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.db = DatabaseManager()
        self.routers = {}  # {router_id: (host, port, public_key)}
        self.clients = {}  # {client_id: public_key}
        
    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Master server listening on {self.host}:{self.port}")
        
        while True:
            client_socket, address = server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()
    
    def handle_client(self, client_socket):
        try:
            data = client_socket.recv(4096).decode()
            message = json.loads(data)
            
            if message['type'] == 'router_register':
                self.register_router(message, client_socket)
            elif message['type'] == 'client_key_request':
                self.send_public_keys(client_socket)
            elif message['type'] == 'get_route':
                self.provide_route(client_socket)
                
        except Exception as e:
            print(f"Master error: {e}")
        finally:
            client_socket.close()
    
    def register_router(self, message, socket):
        router_id = message['router_id']
        self.routers[router_id] = {
            'host': message['host'],
            'port': message['port'],
            'public_key': message['public_key']
        }
        self.db.save_router(router_id, message['public_key'])
        response = {'status': 'registered', 'router_id': router_id}
        socket.send(json.dumps(response).encode())
        print(f"Router {router_id} registered")
    
    def send_public_keys(self, socket):
        response = {
            'type': 'public_keys',
            'routers': self.routers
        }
        socket.send(json.dumps(response).encode())