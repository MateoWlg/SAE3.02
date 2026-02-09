import socket
import sys
import random
import time

sys.path.append('.')
sys.path.append('..')

from config import MASTER_IP, MASTER_PORT, SEPARATOR, BUFFER_SIZE
from core.crypto_simple import encrypt_data

def get_nodes():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((MASTER_IP, MASTER_PORT))
        s.send(f"GET_NODES{SEPARATOR}Client".encode())
        data = s.recv(BUFFER_SIZE).decode()
        s.close()
        
        nodes = []
        if data:
            raw = data.split('|')
            for n in raw:
                parts = n.split(',')
                if len(parts) >= 4:
                    nodes.append({'name': parts[0], 'ip': parts[1], 'port': int(parts[2]), 'key': int(parts[3])})
        return nodes
    except:
        return []

def create_onion(message, circuit, dest_ip, dest_port):
    # 3. Couche FINALE (pour le dernier nœud -> vers Client B)
    payload = f"{dest_ip}|{dest_port}|{message}"
    layer3 = encrypt_data(payload, circuit[2]['key'])
    
    # 2. Couche MILIEU
    payload2 = f"{circuit[2]['ip']}|{circuit[2]['port']}|{layer3}"
    layer2 = encrypt_data(payload2, circuit[1]['key'])
    
    # 1. Couche ENTRÉE
    payload1 = f"{circuit[1]['ip']}|{circuit[1]['port']}|{layer2}"
    layer1 = encrypt_data(payload1, circuit[0]['key'])
    
    return layer1

def start_sender():
    print("[*] Contact Master...")
    nodes = get_nodes()
    if len(nodes) < 3:
        print(f"[!] Pas assez de routeurs ({len(nodes)}/3). Lancez les routeurs !")
        return

    # Sélection de 3 nœuds
    circuit = random.sample(nodes, 3)
    print(f"[+] Circuit : {circuit[0]['name']} -> {circuit[1]['name']} -> {circuit[2]['name']}")

    msg = "Coucou je suis ClientA"
    dest_ip = '192.168.1.12'
    dest_port = 9000

    print("[*] Chiffrement Oignon...")
    onion = create_onion(msg, circuit, dest_ip, dest_port)
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((circuit[0]['ip'], circuit[0]['port']))
        s.send(f"ONION{SEPARATOR}{onion}".encode())
        s.close()
        print("[*] Oignon envoyé !")
    except Exception as e:
        print(f"[!] Erreur envoi : {e}")

def start_receiver():
    ip = '192.168.1.12'
    port = 9000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip, port))
    s.listen(5)
    print(f"[*] Client B (Destinataire) écoute sur {ip}:{port}")
    
    while True:
        conn, addr = s.accept()
        data = conn.recv(BUFFER_SIZE).decode()
        if "ONION" in data:
            data = data.split(SEPARATOR)[1]
        print(f"\n★ MESSAGE REÇU : {data}\n")
        conn.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 client.py [ClientA|ClientB]")
    elif sys.argv[1] == 'ClientA':
        start_sender()
    elif sys.argv[1] == 'ClientB':
        start_receiver()
