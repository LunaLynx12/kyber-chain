from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from blockchain import Blockchain
from pydantic import BaseModel
from user import User
import database
import base64
import time

import hashlib

app = FastAPI(title="Quantum-Safe Chat App")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
chain = Blockchain()
database.init_db()
users = {}

def verify_signature(transaction: dict) -> bool:
    """Verify that the transaction was signed by the owner of the 'from' address."""
    from_address = transaction["from"]
    tx_data = {
        "to": transaction["to"],
        "encrypted_data": transaction["encrypted_data"],
        "timestamp": transaction["timestamp"]
    }

    expected_hash = hashlib.sha256(str(tx_data).encode()).digest()
    
    try:
        public_key_bytes = bytes.fromhex(get_public_key(from_address)["public_key"])
    except Exception as e:
        print("Public key error:", e)
        return False

    # In a real system, use Kyber/ML-KEM or ECDSA to verify signature
    # For now, simulate verification
    return True  # Replace with actual signature check later

class EncryptedData(BaseModel):
    nonce: str
    ciphertext: str

class EncryptedMessage(BaseModel):
    from_user: str
    to_user: str
    encrypted_data: EncryptedData
    signature: str


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/users")
def get_users():
    db_users = database.get_all_users()
    in_memory_users = [(user.name, user.address) for user in users.values()]
    user_addresses = []
    user_addresses.extend(in_memory_users)

    for name in db_users:
        if name not in [u[0] for u in user_addresses]:
            user = User(name)
            user_addresses.append((name, user.address))

    result = [{"name": name, "address": address} for name, address in user_addresses]
    return {"users": result}


@app.post("/register")
def register_user(name: str):
    user = User(name)
    users[user.address] = user
    return {"address": user.address, "public_key": user.keys.public_key.hex(), "private_key": user.keys.private_key.hex()}

@app.post("/register_miner")
def register_miner(name: str):
    try:
        database.add_miner(name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": f"User {name} is now a miner"}

@app.get("/public_key/{address}")
def get_public_key(address: str):
    # First check in-memory users
    for user in users.values():
        if user.address == address:
            return {"public_key": user.keys.public_key.hex()}

    # Then try to load from DB using helper function
    db_user = database.get_user_by_address(address)
    if db_user:
        return {"public_key": db_user["public_key"].hex()}

    raise HTTPException(status_code=404, detail="User not found")


@app.post("/send")
async def send_message(msg: EncryptedMessage):
    # Try to get sender and recipient from in-memory dict
    sender = users.get(msg.from_user)
    recipient = users.get(msg.to_user)

    # If not found, try loading from database
    if not sender:
        db_sender = database.get_user_by_address(msg.from_user)
        if db_sender:
            sender = User(db_sender["name"])
        else:
            raise HTTPException(status_code=400, detail="User not found")

    if not recipient:
        db_recipient = database.get_user_by_address(msg.to_user)
        if db_recipient:
            recipient = User(db_recipient["name"])
        else:
            raise HTTPException(status_code=400, detail="User not found")

    encoded_cyphertext = base64.b64encode(msg.encrypted_data.ciphertext.encode())

    signed_tx = {
        "from": msg.from_user,
        "to": msg.to_user,
        "encrypted_data": {
            "nonce": "dummy",
            "ciphertext": encoded_cyphertext.decode()
        },
        "timestamp": time.time(),
        "signature": msg.signature  # New field
    }

    # Verify signature
    if not verify_signature(signed_tx):
        raise HTTPException(status_code=403, detail="Invalid signature")

    chain.add_transaction(signed_tx)
    return {"status": "Transaction added to pool"}

@app.get("/mine")
def mine(address: str):
    if not chain.unconfirmed_transactions:
        return {"status": "No transactions to mine"}

    # Check if miner is authorized
    if address not in database.get_all_miners():
        raise HTTPException(status_code=403, detail="Unauthorized miner")

    # Mine the block
    proof = chain.mine()

    return {
        "status": "Block mined",
        "hash": proof,
        "transactions": chain.chain[-1].data
    }

@app.get("/read_message/{address}")
def read_messages(address: str):
    # Try to get user from in-memory first
    user = users.get(address)

    # If not found, try loading from DB
    if not user:
        db_user = database.get_user_by_address(address)
        if db_user:
            user = User(db_user["name"])
        else:
            raise HTTPException(status_code=404, detail="User not found")

    # Get user's private key
    private_key_bytes = user.keys.private_key

    # Get chain
    chain_data = chain.to_dict()

    # Filter messages sent to this address
    received_messages = []
    for block in chain_data:
        if block["data"].get("to") == address:
            encrypted_data = block["data"]["encrypted_data"]
            ciphertext = base64.b64decode(encrypted_data["ciphertext"])
            #shared_secret = decapsulate(private_key_bytes, ciphertext)
            #decrypted = decrypt_message(shared_secret, encrypted_data)
            received_messages.append(ciphertext)

    return {"address": address, "received_messages": received_messages}


@app.get("/chain")
def get_chain():
    return chain.to_dict()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)