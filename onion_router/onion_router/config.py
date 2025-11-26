# config.py

# --- ADRESSES IP ET PORTS (À MODIFIER PAR VOS VALEURS DE VM) ---

# IP de la VM hébergeant le Master et la BDD (VM 1)
MASTER_IP = '192.168.1.10' # REMPLACER PAR L'IP RÉELLE DE VOTRE VM MASTER

# Configuration de la BDD MariaDB (Assurez-vous que le user/password est correct)
DB_CONFIG = {
    'host': MASTER_IP, 
    'user': 'onion_user', 
    'password': 'votre_mot_de_passe_secret', # REMPLACER PAR VOTRE MOT DE PASSE BDD
    'database': 'onion_router'
}

MASTER_PORT = 8000 # Port d'écoute du Master

# IP à utiliser par le Client A pour écouter le message final (VM 3)
CLIENT_A_IP = '192.168.1.12' # REMPLACER PAR L'IP RÉELLE DE VOTRE VM CLIENT
CLIENT_A_PORT = 9001

# IP à utiliser par le Client B pour écouter le message final (VM 3)
CLIENT_B_IP = '192.168.1.12' # REMPLACER PAR L'IP RÉELLE DE VOTRE VM CLIENT (peut être la même VM que Client A)
CLIENT_B_PORT = 9002