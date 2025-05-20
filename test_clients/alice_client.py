# alice_client.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from app.kyber_crypto import encapsulate
from app.message import encrypt_message


BASE_URL = "http://localhost:8000"

# Alice's address
alice_address = "0xfb46313bf179a3e5077a924797c7a6a765b394ca"
bob_address = "0x5461bceff435fc33b3da95d27b541b3a39f0131e"


def send_message(from_user, to_user_address, message):
    # Fetch recipient's public key
    response = requests.get(f"{BASE_URL}/public_key/{to_user_address}")
    public_key_hex = response.json()["public_key"]
    public_key_bytes = bytes.fromhex(public_key_hex)

    # Generate shared secret and encrypt message
    shared_secret, ciphertext = encapsulate(public_key_bytes)
    encrypted = encrypt_message(shared_secret, message)

    # Send message
    payload = {
        "from_user": from_user,
        "to_user": to_user_address,
        "encrypted_data": encrypted
    }
    response = requests.post(f"{BASE_URL}/send", json=payload)
    print("Sent:", message)
    print("Response:", response.json())
    return encrypted


if __name__ == "__main__":
    print("Alice sends message to Bob...")
    encrypted_data = send_message(
        alice_address,
        bob_address,
        "Hello Bob, this is quantum-safe!"
    )