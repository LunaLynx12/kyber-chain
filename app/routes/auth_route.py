from fastapi import APIRouter, Request, HTTPException

from fastapi import APIRouter, HTTPException
from user import User
import database

router = APIRouter()
users = {}

@router.get("/resgister", tags=["Auth"], summary="Register a new user")
def register_user(name: str):
    user = User(name)
    users[user.address] = user
    return {
        "address": user.address,
        "public_key": user.keys.public_key.hex(),
        "private_key": user.keys.private_key.hex()  # TODO: ⚠️ REMOVE IN PRODUCTION
    }


@router.get("/users", tags=["Auth"], summary="Get all users")
def get_users(request: Request):
    db_users = database.get_all_users()
    in_memory_users = [
        (user.name, user.address) for user in request.app.state.users.values()
    ]
    user_addresses = list(in_memory_users)

    for name in db_users:
        if name not in [u[0] for u in user_addresses]:
            user = User(name)
            user_addresses.append((name, user.address))

    result = [{"name": name, "address": address} for name, address in user_addresses]
    return {"users": result}


@router.post("/register_miner", tags=["Auth"], summary="Register a new miner")
def register_miner(name: str):
    try:
        database.add_miner(name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": f"User {name} is now a miner"}