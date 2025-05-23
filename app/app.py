from fastapi.middleware.cors import CORSMiddleware
from message import encrypt_message, decrypt_message
from fastapi.responses import RedirectResponse
from kyber_crypto import encapsulate, decapsulate, generate_keypair
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


app = FastAPI(title="Quantum-Safe Blockchain API", version="1.0.0", license_info={"name": "GPL-3.0", "url": "https://www.gnu.org/licenses/gpl-3.0.en.html"})
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
users = {}
app.state.users = users


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


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

@app.post("/send")
async def send_message(msg: EncryptedMessage):
    sender = users.get(msg.from_user)
    recipient = users.get(msg.to_user)

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

    # Load keys
    sender_keys = database.get_user_keys(msg.from_user)
    recipient_pub_key = database.get_user_by_address(msg.to_user)["public_key"]

    # Kyber: Sender encapsulates using recipient's public key
    shared_secret, ciphertext_kyber = encapsulate(recipient_pub_key)    

    encrypted_payload = encrypt_message(
        shared_secret=shared_secret,
        plaintext=msg.encrypted_data.ciphertext
    )

    signed_tx = {
        "from": msg.from_user,
        "to": msg.to_user,
        "kyber_ciphertext": base64.b64encode(ciphertext_kyber).decode(),
        "encrypted_data": {
            "nonce": encrypted_payload["nonce"],
            "ciphertext": encrypted_payload["ciphertext"]
        },
        "timestamp": datetime.utcnow().isoformat(),
        "signature": msg.signature
    }

    # Verify signature
    if not verify_signature(signed_tx):
        raise HTTPException(status_code=403, detail="Invalid signature")

    chain.add_transaction(signed_tx)
    return {"status": "Transaction added to pool"}


@app.get("/read_message/{address}")
def read_messages(address: str):
    user = users.get(address)
    if not user:
        db_user = database.get_user_by_address(address)
        if db_user:
            user = User(db_user["name"])
        else:
            raise HTTPException(status_code=404, detail="User not found")

    # Get user private key
    user_keys = database.get_user_keys(user.name)
    private_key = user_keys["private_key"]

    chain_data = chain.to_dict()  # Should be list of blocks

    received_messages = []
    for block in chain_data:
        if not isinstance(block, dict) or "data" not in block:
            continue

        block_data = block["data"]

        # Handle both single transaction (dict) and list of transactions
        transactions = []
        if isinstance(block_data, dict):
            transactions = [block_data]  # Wrap in list for uniform handling
        elif isinstance(block_data, list):
            transactions = block_data

        for tx in transactions:
            if not isinstance(tx, dict):
                continue

            if tx.get("to") != address:
                continue

            encrypted_data = tx.get("encrypted_data", {})
            ciphertext_b64 = encrypted_data.get("ciphertext")
            nonce_b64 = encrypted_data.get("nonce")
            kyber_ciphertext_b64 = tx.get("kyber_ciphertext")

            if not ciphertext_b64 or not nonce_b64 or not kyber_ciphertext_b64:
                continue

            try:
                kyber_ciphertext = base64.b64decode(kyber_ciphertext_b64)
                print("Kyber ciphertext size:", len(kyber_ciphertext))      # Should be 768
                print("Private key size:", len(private_key))                # Should be 1632
                shared_secret = decapsulate(private_key, kyber_ciphertext)
                print("Shared secret size:", len(shared_secret))            # Should be 32

                decrypted = decrypt_message(shared_secret, {
                    "nonce": nonce_b64,
                    "ciphertext": ciphertext_b64
                })
                received_messages.append(decrypted)
            except Exception as e:
                received_messages.append(f"[Decryption failed: {str(e)}]")

    return {"address": address, "received_messages": received_messages}

if __name__ == "__main__":
    import uvicorn

    database.init_db()
    uvicorn.run(app, host="127.0.0.1", port=8000)