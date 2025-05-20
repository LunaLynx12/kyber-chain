import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def encrypt_message(shared_secret: bytes, plaintext: str) -> dict:
    #aesgcm = AESGCM(shared_secret)
    #nonce = os.urandom(12)  # 96-bit (12-byte) nonce
    #ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    #return {
    #    "nonce": base64.b64encode(nonce).decode(),
    #    "ciphertext": base64.b64encode(ciphertext).decode()
    #}
    return {
        "nonce": "dummy-nonce",
        "ciphertext": plaintext
    }


def decrypt_message(shared_secret: bytes, payload: dict) -> str:
    #aesgcm = AESGCM(shared_secret)
    #nonce = base64.b64decode(payload["nonce"])
    #ciphertext = base64.b64decode(payload["ciphertext"])
    #return aesgcm.decrypt(nonce, ciphertext, None).decode()
    return payload["ciphertext"]