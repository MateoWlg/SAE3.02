import socket
import threading
import sys
sys.path.append('.') # Permet d'importer config et core
from config import MASTER_IP, MASTER_PORT, BUFFER_SIZE, SEPARATOR
from core.crypto_simple import N_MODULE

# Stockage des routeurs : { "Nom": {ip, port, pub_key} }
registry = {}

def handle_node(conn, addr):
    try:
        data = conn.recv(BUFFER_SIZE).decode().strip()
        if not data: return
        
        parts = data.split(SEPARATOR)
        command = parts[0]

        if command == 'REGISTER':
            # Format: REGISTER::::Nom::::IP::::Port::::Key
            name, ip, port, pub_key = parts[1], parts[2], parts[3], parts[4]
            registry[name] = {'ip': ip, 'port': int(port), 'key': pub_key}
            print(f"[+] Routeur enregistré : {name} ({ip}:{port})")
            conn.send("OK".encode())

        elif command == 'GET_NODES':
            # Le client demande la liste des routeurs
            nodes_list = []
            for name, info in registry.items():
                nodes_list.append(f"{name},{info['ip']},{info['port']},{info['key']}")
            response = "|".join(nodes_list)
            conn.send(response.encode())

    except Exception as e:
        print(f"[!] Erreur : {e}")
    finally:
        conn.close()

def start_master():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((MASTER_IP, MASTER_PORT))
    server.listen(5)
    print(f"[*] MASTER (Annuaire) démarré sur {MASTER_IP}:{MASTER_PORT}")
    
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_node, args=(conn, addr)).start()

if __name__ == '__main__':
    start_master()
