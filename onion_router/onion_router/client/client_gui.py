import tkinter as tk
from tkinter import scrolledtext, messagebox
import socket
import sys
import random
import threading

# On récupère ta config existante
sys.path.append('.')
from config import MASTER_IP, MASTER_PORT, SEPARATOR, BUFFER_SIZE
from core.crypto_simple import encrypt_data

class OnionClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Onion Router - Client Envoyeur")
        self.root.geometry("500x400")
        self.root.configure(bg="#2c3e50")

        # Titre
        self.label = tk.Label(root, text="Messagerie Sécurisée (Oignon)", 
                              font=("Arial", 14, "bold"), fg="white", bg="#2c3e50")
        self.label.pack(pady=10)

        # Zone de saisie
        self.msg_entry = tk.Entry(root, width=40, font=("Arial", 12))
        self.msg_entry.pack(pady=5)
        self.msg_entry.insert(0, "Message secret...")

        # Bouton Envoyer
        self.send_btn = tk.Button(root, text="ENVOYER LE MESSAGE", 
                                  command=self.send_message, 
                                  bg="#27ae60", fg="white", font=("Arial", 12, "bold"))
        self.send_btn.pack(pady=10)

        # Log visuel
        self.log_area = scrolledtext.ScrolledText(root, width=50, height=15, bg="black", fg="#00ff00")
        self.log_area.pack(pady=10)

    def log(self, text):
        self.log_area.insert(tk.END, text + "\n")
        self.log_area.see(tk.END)

    def get_nodes(self):
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
                        nodes.append({'name': parts[0], 'ip': parts[1], 
                                      'port': int(parts[2]), 'key': int(parts[3])})
            return nodes
        except Exception as e:
            self.log(f"[ERREUR] Impossible de joindre le Master: {e}")
            return []

    def create_onion(self, message, circuit, dest_ip, dest_port):
        # Couche 3
        payload = f"{dest_ip}|{dest_port}|{message}"
        layer3 = encrypt_data(payload, circuit[2]['key'])
        # Couche 2
        payload2 = f"{circuit[2]['ip']}|{circuit[2]['port']}|{layer3}"
        layer2 = encrypt_data(payload2, circuit[1]['key'])
        # Couche 1
        payload1 = f"{circuit[1]['ip']}|{circuit[1]['port']}|{layer2}"
        layer1 = encrypt_data(payload1, circuit[0]['key'])
        return layer1

    def send_message(self):
        message = self.msg_entry.get()
        if not message: return

        self.log(f"[*] Récupération des nœuds...")
        nodes = self.get_nodes()
        
        if len(nodes) < 3:
            self.log(f"[!] Erreur: Pas assez de routeurs ({len(nodes)}/3)")
            messagebox.showerror("Erreur", "Pas assez de routeurs connectés !")
            return

        circuit = random.sample(nodes, 3)
        circuit_str = f"{circuit[0]['name']} -> {circuit[1]['name']} -> {circuit[2]['name']}"
        self.log(f"[+] Circuit : {circuit_str}")

        dest_ip = '192.168.1.12'
        dest_port = 9000

        self.log("[*] Chiffrement en couches...")
        onion = self.create_onion(message, circuit, dest_ip, dest_port)
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((circuit[0]['ip'], circuit[0]['port']))
            s.send(f"ONION{SEPARATOR}{onion}".encode())
            s.close()
            self.log("[OK] Message envoyé dans le réseau !")
            self.msg_entry.delete(0, tk.END)
        except Exception as e:
            self.log(f"[!] Erreur d'envoi : {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = OnionClientGUI(root)
    root.mainloop()