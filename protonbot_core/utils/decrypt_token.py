from base64 import urlsafe_b64decode
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

def decrypt_token(encrypted_token, password):
    data = urlsafe_b64decode(encrypted_token.encode())
    salt, iv, tag, ciphertext = data[:16], data[16:28], data[28:44], data[44:]
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
        backend=default_backend()
    ).decryptor()
    decrypted_token = decryptor.update(ciphertext) + decryptor.finalize()
    return decrypted_token.decode()