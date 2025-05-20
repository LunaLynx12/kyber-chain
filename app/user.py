import hashlib
from kyber_crypto import generate_keypair


class User:
    def __init__(self, name):
        self.name = name
        self.keys = generate_keypair()
        # Generate an address from public key hash
        public_key_hash = hashlib.sha256(self.keys.public_key).digest()
        self.address = "0x" + public_key_hash.hex()[-40:]  # Ethereum-style address