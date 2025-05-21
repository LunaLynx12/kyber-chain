from kyber_py.kyber import Kyber512
from dataclasses import dataclass


@dataclass
class KeyPair:
    public_key: bytes
    private_key: bytes


def generate_keypair():
    """Generate a Kyber512 keypair."""
    pk, sk = Kyber512.keygen()
    return KeyPair(public_key=pk, private_key=sk)


def encapsulate(public_key: bytes) -> tuple[bytes, bytes]:
    """
    Encapsulate a shared secret using the given public key.
    
    Returns:
        (shared_secret, ciphertext)
    """
    shared_secret, ciphertext = Kyber512.encaps(public_key)
    return shared_secret, ciphertext


def decapsulate(private_key: bytes, ciphertext: bytes) -> bytes:
    """
    Decapsulate the shared secret using the private key and ciphertext.
    """
    return Kyber512.decaps(private_key, ciphertext)