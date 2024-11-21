from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import os
import base64

def encrypt_token(token, password):
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    iv = os.urandom(12)
    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=default_backend()
    ).encryptor()
    encrypted_token = encryptor.update(token.encode()) + encryptor.finalize()
    return base64.urlsafe_b64encode(salt + iv + encryptor.tag + encrypted_token).decode()

def save_encrypted_token(encrypted_token):
    with open('.env', 'w') as file:
        file.write(f'ENCRYPTED_TOKEN={encrypted_token}\n')

if __name__ == "__main__":
    token = input("Enter your Discord bot token: ")
    password = input("Enter a password to encrypt the token: ")
    encrypted_token = encrypt_token(token, password)
    save_encrypted_token(encrypted_token)
    print("Token encrypted and saved to .env file.")