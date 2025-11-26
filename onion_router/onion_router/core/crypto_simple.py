import random
import math

# =================================================================
# PARAMÈTRES SIMPLIFIÉS DE CRYPTOGRAPHIE ASYMÉTRIQUE
# Ces valeurs sont publiques et connues de tous les composants
# =================================================================
# N_MODULE doit être un nombre premier (pour simplifier le calcul de phi(N) = N-1)
# Pour une implémentation réelle, choisir un nombre beaucoup plus grand (2048 bits ou plus)
N_MODULE = 9973
# E_COEFFICIENT (l'exposant public) doit être premier avec phi(N)
E_COEFFICIENT = 3


def generate_keys():
    """
    Génère une paire de clés (Privée, Publique) pour un Routeur.
    
    La clé publique est le coefficient E. La clé privée est l'inverse modulaire de E.
    """
    # 1. Calcul de l'indicatrice d'Euler phi(N) = N - 1 (car N est premier)
    phi_N = N_MODULE - 1
    
    K_publique = E_COEFFICIENT
    
    # 2. Clé Privée (K_Privée ou 'D') : l'inverse modulaire de K_publique mod phi_N
    # K_Privée est le secret du Routeur pour déchiffrer.
    try:
        # Vérification nécessaire pour s'assurer que l'inverse existe (PGCD(E, phi_N) = 1)
        if math.gcd(K_publique, phi_N) != 1:
             raise ValueError("E_COEFFICIENT et phi(N) ne sont pas premiers entre eux.")
             
        # pow(a, -1, m) calcule l'inverse modulaire de 'a' modulo 'm'
        K_privee = pow(K_publique, -1, phi_N)
        
    except ValueError as e:
        print(f"Erreur de conception dans la cryptographie : {e}")
        return None, None, None

    return K_privee, K_publique, N_MODULE

# -----------------------------------------------------------------
# Fonctions de Chiffrement/Déchiffrement (Type RSA Simulé)
# -----------------------------------------------------------------

def encrypt_data(data_int, K_public):
    """
    Chiffre une donnée (entier) en utilisant la clé publique du Routeur (K_public).
    (Opération effectuée par le Client)
    
    C = M^e mod N
    """
    if data_int >= N_MODULE:
        # En cas de message trop grand, le découpage sera géré plus tard.
        # Ici, nous nous assurons que le message n'est pas supérieur au module N.
        data_int = data_int % N_MODULE
        
    # Chiffrement: (message ** K_public) % N_MODULE
    ciphertext = pow(data_int, K_public, N_MODULE)
    return ciphertext

def decrypt_data(ciphertext_int, K_private):
    """
    Déchiffre une donnée (entier) en utilisant la clé privée du Routeur (K_private).
    (Opération effectuée par le Routeur)
    
    M = C^d mod N
    """
    # Déchiffrement: (ciphertext ** K_private) % N_MODULE
    decrypted_data = pow(ciphertext_int, K_private, N_MODULE)
    return decrypted_data


# =================================================================
# Fonctions de conversion (Le vrai chiffrement se fait sur des données brutes/textes)
# =================================================================

def text_to_int(text):
    """Convertit une chaîne de caractères en un grand entier pour le chiffrement."""
    # Encodage en bytes, puis conversion en entier (big-endian)
    return int.from_bytes(text.encode('utf-8'), byteorder='big')

def int_to_text(data_int):
    """Convertit un grand entier déchiffré en chaîne de caractères."""
    # Conversion en bytes, puis décodage en chaîne
    return data_int.to_bytes((data_int.bit_length() + 7) // 8, byteorder='big').decode('utf-8', errors='ignore').strip('\x00')