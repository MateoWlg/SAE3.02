import socket
import threading
import sys
import time

sys.path.append('.')
sys.path.append('..')

from config import MASTER_IP, MASTER_PORT, SEPARATOR, BUFFER_SIZE
from core.crypto_simple import generate_keys, decrypt_data, N_MODULE

class Router:
    def __init__(self, name, listen_port, listen_ip):
        self.name = name
        self.ip = listen_ip
        self.port = int(listen_port)
        self.private_key, self.public_key, self.mod = generate_keys()
        
    def register(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((MASTER_IP, MASTER_PORT))
            key_val = str(self.public_key[0])
            msg = f"REGISTER{SEPARATOR}{self.name}{SEPARATOR}{self.ip}{SEPARATOR}{self.port}{SEPARATOR}{key_val}"
            s.send(msg.encode())
            s.close()
            print(f"[+] Enregistré au Master avec succès.")
        except Exception as e:
            print(f"[!] Erreur connexion Master : {e}")

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.ip, self.port))
        server.listen(5)
        print(f"[*] {self.name} écoute sur {self.ip}:{self.port}")
        
        while True:
            conn, addr = server.accept()
            threading.Thread(target=self.handle, args=(conn,)).start()

    def handle(self, conn):
        try:
            data = conn.recv(BUFFER_SIZE).decode().strip()
            if not data: return
            parts = data.split(SEPARATOR)
            
            if parts[0] == 'ONION':
                encrypted = parts[1]
                print(f"--- Paquet reçu ({len(encrypted)} bytes) ---")
                
                # Déchiffrement
                decrypted = decrypt_data(encrypted, self.private_key)
                
                # Routage
                try:
                    # On splitte seulement 2 fois pour garder le payload intact
                    next_ip, next_port, payload = decrypted.split('|', 2)
                    print(f"    [=>] Relais vers {next_ip}:{next_port}")
                    self.forward(next_ip, int(next_port), payload)
                except ValueError:
                    print(f"    [★] ARRIVÉE : {decrypted}")

        except Exception as e:
            print(f"[!] Erreur : {e}")
        finally:
            conn.close()

    def forward(self, ip, port, payload):
        try:
            time.sleep(0.5) 
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            msg = f"ONION{SEPARATOR}{payload}"
            s.send(msg.encode())
            s.close()
        except Exception as e:
            print(f"[!] Erreur relais : {e}")

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python3 router.py <Nom> <Port> <IP>")
    else:
        r = Router(sys.argv[1], sys.argv[2], sys.argv[3])
        r.register()
        r.start()
