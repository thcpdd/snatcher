import base64
import hashlib
from time import time
from random import randint

from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes


def encrypt_fuel(row_id: str, key: str):
    nonce = get_random_bytes(12)
    key = base64.b64decode(key.encode())
    cipher = ChaCha20.new(key=key, nonce=nonce)
    sign = str(int(time())) + str(randint(1000, 9999)) + row_id
    ciphertext = cipher.encrypt(sign.encode())
    fuel = base64.b64encode(nonce + ciphertext)
    return fuel.decode()


def decrypt_fuel(fuel: str, key: str):
    bytes_fuel = base64.b64decode(fuel.encode())
    key = base64.b64decode(key.encode())
    nonce, ciphertext = bytes_fuel[:12], bytes_fuel[12:]
    cipher = ChaCha20.new(key=key, nonce=nonce)
    sign = cipher.decrypt(ciphertext)
    return sign[-24:].decode()


def password_hash(password: str, salt: str):
    salt = base64.b64decode(salt.encode())
    password = password.encode()
    hashed = hashlib.pbkdf2_hmac('sha256', password, salt, 100000)
    store_password = salt + hashed
    return base64.b64encode(store_password).decode()


if __name__ == '__main__':
    print(base64.b64encode(get_random_bytes(32)))
