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
    s.bind((HOST, PORT))
    s.listen(1)
    print("[Server] Listening for client...")

    conn, addr = s.accept()
    with conn:
        print(f"[Server] Connected by {addr}")

        # Step 1: Generate keypair
        pk, sk = Kyber512.keygen()
        print(f"[Server] Public key size: {len(pk)} bytes")

        # Step 2: Send public key to client
        send_bytes(conn, pk)
        print(f"[Server] Sent public key ({len(pk)} bytes)")

        # Step 3: Receive ciphertext
        ciphertext = recv_bytes(conn)
        print(f"[Server] Received ciphertext ({len(ciphertext)} bytes)")

        # ML-KEM-512 expects exactly 768-byte ciphertext
        if len(ciphertext) != 768:
            print(f"[Server] Warning: Expected 768-byte ciphertext, got {len(ciphertext)} bytes. Truncating.")
            ciphertext = ciphertext[:768]

        # Step 4: Decapsulate to get shared secret
        shared_secret = Kyber512.decaps(sk, ciphertext)
        print(f"[Server] Shared secret: {shared_secret.hex()[:64]}...")

        # Step 5: Receive nonce and encrypted message
        nonce = recv_bytes(conn)
        encrypted_message = recv_bytes(conn)

        # Step 6: Decrypt message
        aesgcm = AESGCM(shared_secret[:16])
        decrypted_message = aesgcm.decrypt(nonce, encrypted_message, None)

        print(f"[Server] Received message: {decrypted_message.decode('utf-8')}")