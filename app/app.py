from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from user import User
from kyber_crypto import generate_keypair, encapsulate, decapsulate
from message import encrypt_message, decrypt_message
from blockchain import Blockchain
import base64
import time


app = FastAPI(title="Quantum-Safe Chat App")

# Simulated users
alice = User("Alice")
bob = User("Bob")

users = {
    alice.address: alice,
    bob.address: bob,
}

class EncryptedData(BaseModel):
    nonce: str
    ciphertext: str

class EncryptedMessage(BaseModel):
    from_user: str
    to_user: str
    encrypted_data: EncryptedData


chain = Blockchain()

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

@app.get("/users")
def get_users():
    return list(users.keys())

@app.post("/register")
def register_user(name: str):
    user = User(name)
    users[user.address] = user
    return {"address": user.address}

@app.get("/public_key/{address}")
def get_public_key(address: str):
    user = users.get(address)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"public_key": user.keys.public_key.hex()}

@app.get("/private_keys")
def get_private_keys():
    return {
        "Alice": alice.keys.private_key.hex(),
        "Bob": bob.keys.private_key.hex()
    }

@app.post("/send")
async def send_message(msg: EncryptedMessage):
    sender = users.get(msg.from_user)
    recipient = users.get(msg.to_user)

    if not sender or not recipient:
        raise HTTPException(status_code=400, detail="User not found")

    chain.add_block({
        "from": msg.from_user,
        "to": msg.to_user,
        "encrypted_data": {
        #    "nonce": msg.encrypted_data.nonce,
        #    "ciphertext": msg.encrypted_data.ciphertext
            "nonce": "dummy",
            "ciphertext": msg.encrypted_data.ciphertext
        },
        "timestamp": time.time(),
    })

    return {"status": "Message sent", "hash": msg.encrypted_data.ciphertext}

@app.get("/read_message/{address}")
def read_messages(address: str):
    user = users.get(address)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get user's private key
    #private_key_bytes = user.keys.private_key

    # Get chain
    chain_data = chain.to_dict()

    # Filter messages sent to this address
    received_messages = []
    for block in chain_data:
        if block["data"].get("to") == address:
            #encrypted_data = block["data"]["encrypted_data"]
            #ciphertext = base64.b64decode(encrypted_data["ciphertext"])
            #shared_secret = decapsulate(private_key_bytes, ciphertext)
            #decrypted = decrypt_message(shared_secret, encrypted_data)
            #received_messages.append(decrypted)
            received_messages.append(block["data"]["encrypted_data"]["ciphertext"])

    return {"address": address, "received_messages": received_messages}

@app.get("/chain")
def get_chain():
    return chain.to_dict()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)