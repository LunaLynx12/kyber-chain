from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from routes import chain_route as chain_routes
from routes import mine_route as mine_routes
from routes import auth_route as auth_routes
from fastapi import FastAPI, HTTPException
from blockchain import Blockchain
from pydantic import BaseModel
from datetime import datetime
from user import User
import database
import base64

users = {}
app = FastAPI(title="Quantum-Safe Chat App")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chain_routes.router)
app.include_router(mine_routes.router)
app.include_router(auth_routes.router)

chain = Blockchain()
app.state.chain = chain
app.state.users = users

database.init_db()


def verify_signature(transaction: dict) -> bool:
    """Verify that the transaction was signed by the owner of the 'from' address."""
    from_address = transaction["from"]
    tx_data = {
        "to": transaction["to"],
        "encrypted_data": transaction["encrypted_data"],
        "timestamp": transaction["timestamp"]
    }

    return True  # Replace with actual signature check later

class EncryptedData(BaseModel):
    nonce: str
    ciphertext: str

class EncryptedMessage(BaseModel):
    from_user: str
    to_user: str
    encrypted_data: EncryptedData
    signature: str

def get_public_key_bytes(address: str) -> bytes:
    user = users.get(address)
    if user:
        return user.keys.public_key
    db_user = database.get_user_by_address(address)
    if db_user:
        return db_user["public_key"]
    raise HTTPException(status_code=404, detail="User not found")


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


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
        "timestamp": datetime.utcnow().isoformat(),
        "signature": msg.signature  # New field
    }

    # Verify signature
    if not verify_signature(signed_tx):
        raise HTTPException(status_code=403, detail="Invalid signature")

    chain.add_transaction(signed_tx)
    return {"status": "Transaction added to pool"}

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

    # Get chain
    chain_data = chain.to_dict()

    # Filter messages sent to this address
    received_messages = []
    for block in chain_data:
        if block["data"].get("to") == address:
            encrypted_data = block["data"]["encrypted_data"]
            ciphertext = base64.b64decode(encrypted_data["ciphertext"])
            received_messages.append(ciphertext)

    return {"address": address, "received_messages": received_messages}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)