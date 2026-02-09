import random
import sys

# Module public partagé (Indispensable pour le Master)
N_MODULE = 1000  

def generate_keys():
    """Génère une paire de clés publique/privée simplifiée"""
    n = N_MODULE
    e = random.randint(100, 999) 
    d = e # En XOR symétrique, la clé de déchiffrement est la même
    return ((d, n), (e, n), n)

def encrypt_data(message, public_key_tuple):
    """Chiffre le message avec XOR"""
    if isinstance(public_key_tuple, tuple): key = public_key_tuple[0]
    else: key = public_key_tuple
    
    if isinstance(message, int): message = str(message)
    
    encrypted_chars = []
    for char in message:
        # Opération XOR simple et robuste
        enc_val = ord(char) ^ (key % 255)
        encrypted_chars.append(str(enc_val))
    return "-".join(encrypted_chars)

def decrypt_data(ciphertext, private_key_tuple):
    """Déchiffre le message"""
    if isinstance(private_key_tuple, tuple): key = private_key_tuple[0]
    else: key = private_key_tuple
        
    try:
        parts = ciphertext.split('-')
        decrypted_chars = []
        for p in parts:
            if not p: continue
            dec_val = int(p)
            char_code = dec_val ^ (key % 255)
            decrypted_chars.append(chr(char_code))
        return "".join(decrypted_chars)
    except:
        return ""

# Fonctions de compatibilité (si besoin)
def text_to_int(text): return text
def int_to_text(text): return text
