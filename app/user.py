from database import get_user_keys, add_user
from kyber_crypto import generate_keypair
from dataclasses import dataclass
import hashlib

class User:
    def __init__(self, name):
        self.name = name
        self.keys = self._get_or_generate_keypair()

        public_key_hash = hashlib.sha256(self.keys.public_key).digest()
        self.address = "0x" + public_key_hash.hex()[-40:]

    def _get_or_generate_keypair(self):
        """Get or generate keypair for the user."""
        db_keys = get_user_keys(self.name)

        if db_keys:
            return KeyPair(
                public_key=db_keys["public_key"],
                private_key=db_keys["private_key"]
            )

        keypair = generate_keypair()
        add_user(self.name, keypair.public_key, keypair.private_key)
        return keypair


@dataclass
class KeyPair:
    public_key: bytes
    private_key: bytes