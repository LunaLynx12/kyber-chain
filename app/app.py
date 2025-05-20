from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from user import User
import database
from kyber_crypto import generate_keypair, encapsulate, decapsulate
from message import encrypt_message, decrypt_message
from blockchain import Blockchain
import time
import base64


app = FastAPI(title="Quantum-Safe Chat App")
chain = Blockchain()
database.init_db()
users = {}


class EncryptedData(BaseModel):
    nonce: str
    ciphertext: str

class EncryptedMessage(BaseModel):
    from_user: str
    to_user: str
    encrypted_data: EncryptedData


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
    return {"address": user.address}


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

    chain.add_block({
        "from": msg.from_user,
        "to": msg.to_user,
        "encrypted_data": {
            "nonce": "dummy",
            "ciphertext": encoded_cyphertext
        },
        "timestamp": time.time(),
    })

    return {"status": "Message sent", "hash": encoded_cyphertext.hex()}
    #{
    #   "status": "Message sent",
    #   "hash": "534756736247387349466476636d786b49513d3d"
    #}

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