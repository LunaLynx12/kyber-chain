from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from database import get_miner_key
import hashlib

api_key_header = APIKeyHeader(name="Authorization", auto_error=True)

def verify_api_key(name: str, authorization: str = Depends(api_key_header)):
    hashed_key = get_miner_key(name)
    if not hashed_key or hashed_key != hashlib.sha256(authorization.encode()).hexdigest():
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return authorization
