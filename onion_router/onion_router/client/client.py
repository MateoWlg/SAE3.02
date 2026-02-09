import socket
import sys
import random

sys.path.append('.')
sys.path.append('..')

from config import MASTER_IP, MASTER_PORT, SEPARATOR, BUFFER_SIZE
from core.crypto_simple import encrypt_data

def get_nodes():
    """Récupère la liste des nœuds depuis le Master"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((MASTER_IP, MASTER_PORT))
    s.send(f"GET_NODES{SEPARATOR}Client".encode())
    data = s.recv(BUFFER_SIZE).decode()
    s.close()
    
    nodes = []
    if data:
        raw_nodes = data.split('|')
        for n in raw_nodes:
            # Format: nom,ip,port,key
            parts = n.split(',')
            nodes.append({'name': parts[0], 'ip': parts[1], 'port': int(parts[2]), 'key': int(parts[3])})
    return nodes

def create_onion(message, circuit, recipient_ip, recipient_port):
    """Encapsule le message dans 3 couches (Oignon)"""
    # 3. Couche INTÉRIEURE (Pour le dernier nœud -> vers Client B)
    # Le dernier nœud doit voir : IP_B|Port_B|Message_Clair
    payload = f"{recipient_ip}|{recipient_port}|{message}"
    # On chiffre avec la clé du nœud de sortie (le dernier du circuit)
    encrypted_layer3 = encrypt_data(payload, circuit[2]['key'])
    
    # 2. Couche MILIEU (Pour le 2ème nœud -> vers le 3ème)
    # Le 2ème nœud doit voir : IP_Node3|Port_Node3|Layer3
    payload_2 = f"{circuit[2]['ip']}|{circuit[2]['port']}|{encrypted_layer3}"
    encrypted_layer2 = encrypt_data(payload_2, circuit[1]['key'])
    
    # 1. Couche EXTÉRIEURE (Pour le 1er nœud -> vers le 2ème)
    # Le 1er nœud doit voir : IP_Node2|Port_Node2|Layer2
    payload_1 = f"{circuit[1]['ip']}|{circuit[1]['port']}|{encrypted_layer2}"
    encrypted_layer1 = encrypt_data(payload_1, circuit[0]['key'])
    
    return encrypted_layer1

def start_sender():
    print("[*] Téléchargement de l'annuaire...")
    nodes = get_nodes()
    if len(nodes) < 3:
        print(f"[!] Pas assez de nœuds actifs ({len(nodes)}/3 min). Lancez les routeurs !")
        return

    # Sélectionner 3 nœuds au hasard
    circuit = random.sample(nodes, 3)
    print(f"[+] Circuit choisi : {circuit[0]['name']} -> {circuit[1]['name']} -> {circuit[2]['name']}")

    message = "Coucou je suis ClientA"
    # Destination finale (Client B sur VM 3)
    dest_ip = '192.168.1.12' 
    dest_port = 9000

    print("[*] Construction de l'oignon...")
    onion = create_onion(message, circuit, dest_ip, dest_port)
    
    # Envoyer au premier nœud
    entry_node = circuit[0]
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((entry_node['ip'], entry_node['port']))
        msg = f"ONION{SEPARATOR}{onion}"
        s.send(msg.encode())
        s.close()
        print("[*] Oignon envoyé !")
    except Exception as e:
        print(f"[!] Erreur envoi : {e}")

def start_receiver():
    # Le Client B écoute sur le port 9000 (comme défini dans create_onion)
    ip = '192.168.1.12' # IP de la VM 3
    port = 9000
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip, port))
    s.listen(5)
    print(f"[*] Client B en attente sur {ip}:{port}...")
    
    while True:
        conn, addr = s.accept()
        data = conn.recv(BUFFER_SIZE).decode()
        # Le dernier routeur envoie souvent avec le préfixe ONION, ou brut.
        # On nettoie si besoin.
        if "ONION" in data:
            data = data.split(SEPARATOR)[1]
            
        print(f"\n★ REÇU : {data}\n")
        conn.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 client.py [ClientA|ClientB]")
    elif sys.argv[1] == 'ClientA':
        start_sender()
    elif sys.argv[1] == 'ClientB':
        start_receiver()
