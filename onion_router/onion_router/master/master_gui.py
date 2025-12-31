import tkinter as tk
from tkinter import scrolledtext, ttk
import socket
import threading
import sys

# On reprend ta config
sys.path.append('.')
from config import MASTER_IP, MASTER_PORT, SEPARATOR, BUFFER_SIZE
from core.db_manager import save_node_to_db, load_nodes_from_db

class MasterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MASTER - Annuaire Central")
        self.root.geometry("600x500")
        self.root.configure(bg="#2c3e50")

        # Titre
        tk.Label(root, text="ANNUAIRE DES ROUTEURS (TOR)", 
                 font=("Arial", 16, "bold"), fg="#ecf0f1", bg="#2c3e50").pack(pady=10)

        # Tableau des nœuds connectés
        columns = ("nom", "ip", "port")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", height=8)
        self.tree.heading("nom", text="Nom du Routeur")
        self.tree.heading("ip", text="Adresse IP")
        self.tree.heading("port", text="Port")
        
        self.tree.column("nom", width=150)
        self.tree.column("ip", width=150)
        self.tree.column("port", width=100)
        self.tree.pack(pady=10)

        # Zone de logs
        self.log_area = scrolledtext.ScrolledText(root, width=70, height=12, bg="black", fg="#00ff00")
        self.log_area.pack(pady=10)

        # Chargement de la base de données existante
        self.registry = load_nodes_from_db()
        self.refresh_table()

        # Démarrage du serveur dans un Thread séparé (pour pas bloquer l'interface)
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.daemon = True
        self.server_thread.start()

    def log(self, text):
        self.log_area.insert(tk.END, text + "\n")
        self.log_area.see(tk.END)

    def refresh_table(self):
        # On vide et on remplit
        for item in self.tree.get_children():
            self.tree.delete(item)
        for name, info in self.registry.items():
            self.tree.insert("", tk.END, values=(name, info['ip'], info['port']))

    def start_server(self):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((MASTER_IP, MASTER_PORT))
            server.listen(5)
            self.log(f"[*] MASTER DÉMARRÉ SUR {MASTER_IP}:{MASTER_PORT}")
            self.log(f"[*] En attente des routeurs...")

            while True:
                conn, addr = server.accept()
                threading.Thread(target=self.handle_node, args=(conn,)).start()
        except Exception as e:
            self.log(f"[CRASH] Erreur serveur : {e}")

    def handle_node(self, conn):
        try:
            data = conn.recv(BUFFER_SIZE).decode().strip()
            if not data: return
            
            parts = data.split(SEPARATOR)
            command = parts[0]

            if command == 'REGISTER':
                name, ip, port, key = parts[1], parts[2], parts[3], parts[4]
                
                # Mise à jour mémoire + DB + Interface
                self.registry[name] = {'ip': ip, 'port': int(port), 'key': key}
                save_node_to_db(name, ip, port, key)
                
                # Mise à jour visuelle (depuis le thread principal c'est mieux mais ça passe ici)
                self.root.after(0, self.refresh_table)
                self.root.after(0, lambda: self.log(f"[+] NOUVEAU NOEUD : {name} ({ip})"))
                
                conn.send("OK".encode())

            elif command == 'GET_NODES':
                nodes_list = []
                for name, info in self.registry.items():
                    nodes_list.append(f"{name},{info['ip']},{info['port']},{info['key']}")
                response = "|".join(nodes_list)
                conn.send(response.encode())
                self.log(f"[?] Un client a demandé l'annuaire.")

        except Exception as e:
            self.log(f"[!] Erreur : {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = MasterGUI(root)
    root.mainloop()