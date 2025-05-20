from kyber_py.ml_kem import ML_KEM_512
from dataclasses import dataclass


@dataclass
class KeyPair:
    public_key: bytes
    private_key: bytes


def generate_keypair():
    ek, dk = ML_KEM_512.keygen()
    return KeyPair(public_key=ek, private_key=dk)


def encapsulate(public_key: bytes) -> tuple:
    secret, ct = ML_KEM_512.encaps(public_key)
    return secret, ct


def decapsulate(private_key: bytes, ciphertext: bytes) -> bytes:
    return ML_KEM_512.decaps(private_key, ciphertext)