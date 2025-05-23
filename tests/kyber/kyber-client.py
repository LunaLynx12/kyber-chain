import socket
from kyber_py.kyber import Kyber512
import struct
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def send_bytes(sock, data: bytes):
    sock.sendall(struct.pack('>I', len(data)))
    sock.sendall(data)

def recv_bytes(sock) -> bytes:
    raw_len = sock.recv(4)
    if not raw_len:
        raise ConnectionError("Connection closed while reading length")
    length = struct.unpack('>I', raw_len)[0]
    data = b''
    while len(data) < length:
        packet = sock.recv(length - len(data))
        if not packet:
            raise ConnectionError("Connection closed while reading data")
        data += packet
    return data

HOST = '127.0.0.1'
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print("[Client] Connected to server.")

    # Step 1: Receive public key
    public_key = recv_bytes(s)
    print(f"[Client] Received public key ({len(public_key)} bytes)")

    # Step 2: Encapsulate to get shared secret and ciphertext
    shared_secret, ciphertext = Kyber512.encaps(public_key)
    print(f"[Client] Ciphertext length: {len(ciphertext)} bytes")
    print(f"[Client] Shared secret: {shared_secret.hex()[:64]}...")

    # Step 3: Send ciphertext to server
    send_bytes(s, ciphertext)
    print("[Client] Sent ciphertext.")

    # Step 4: Use shared secret for symmetric encryption
    aesgcm = AESGCM(shared_secret[:16])  # AES-128-GCM uses 16-byte key
    nonce = b'1234567890ab'  # Should be random and unique per message
    message = b"Hello world from the quantum-safe client!"

    # Encrypt the message
    encrypted_message = aesgcm.encrypt(nonce, message, None)

    # Step 5: Send encrypted message and nonce
    send_bytes(s, nonce)
    send_bytes(s, encrypted_message)

    print(f"[Client] Sent encrypted message of size {len(encrypted_message)} bytes.")