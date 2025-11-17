import random
import math

class RSACustom:
    def __init__(self, key_size=64):
        self.key_size = key_size  # Petit pour la démo
    
    def is_prime(self, n):
        if n < 2:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True
    
    def generate_prime(self):
        while True:
            num = random.randint(2**(self.key_size-1), 2**self.key_size-1)
            if self.is_prime(num):
                return num
    
    def gcd(self, a, b):
        while b != 0:
            a, b = b, a % b
        return a
    
    def mod_inverse(self, a, m):
        # Algorithme d'Euclide étendu
        m0, x0, x1 = m, 0, 1
        if m == 1:
            return 0
        while a > 1:
            q = a // m
            m, a = a % m, m
            x0, x1 = x1 - q * x0, x0
        if x1 < 0:
            x1 += m0
        return x1
    
    def generate_keys(self):
        p = self.generate_prime()
        q = self.generate_prime()
        while p == q:
            q = self.generate_prime()
        
        n = p * q
        phi = (p - 1) * (q - 1)
        
        # Choisir e
        e = random.randint(2, phi - 1)
        while self.gcd(e, phi) != 1:
            e = random.randint(2, phi - 1)
        
        # Calculer d
        d = self.mod_inverse(e, phi)
        
        public_key = (e, n)
        private_key = (d, n)
        
        return private_key, public_key
    
    def encrypt(self, message, public_key):
        e, n = public_key
        encrypted = []
        for char in message:
            encrypted.append(pow(ord(char), e, n))
        return encrypted
    
    def decrypt(self, encrypted_message, private_key):
        d, n = private_key
        decrypted = []
        for num in encrypted_message:
            decrypted.append(chr(pow(num, d, n)))
        return ''.join(decrypted)