import requests
import base64
from datetime import datetime

BLOCKCHAIN_URL = "http://localhost:8000/send"
PRIVATE_KEY = "dummy_private_key"

def send_encrypted_message(from_addr, to_addr, plaintext: str):
    # Simulate encryption: we'll base64 encode as a placeholder
    ciphertext = base64.b64encode(plaintext.encode()).decode()

    tx_payload = {
        "from_user": from_addr,
        "to_user": to_addr,
        "encrypted_data": {
            "nonce": "dummy",
            "ciphertext": ciphertext
        },
        "timestamp": datetime.utcnow().isoformat(),
        "signature": "dummy"
    }

    try:
        response = requests.post(BLOCKCHAIN_URL, json=tx_payload)
        if response.status_code == 200:
            print("✅ Message sent successfully:", response.json())
        else:
            print(f"❌ Failed to send message. Status {response.status_code}")
            print("Response:", response.text)
    except requests.exceptions.RequestException as e:
        print("🚫 Request failed:", e)

if __name__ == "__main__":
    # Replace with actual blockchain user addresses
    sender_address = "0xeadf19d078cd4419345280967470eca02cfa8614"
    recipient_address = "0x7e029943b2593b8001b6b85c7f2a411e10d94888"
    message = "Message to be sent"

    send_encrypted_message(sender_address, recipient_address, message)
