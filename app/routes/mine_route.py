from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.security import APIKeyHeader
from database import get_all_miners
from security import verify_api_key

router = APIRouter()
api_key_header = APIKeyHeader(name="Authorization", auto_error=True)

@router.get("/mine", tags=["Blockchain"], summary="Mine a new block")
def mine(
    name: str,
    request: Request,
    _ = Depends(verify_api_key)
):
    chain = request.app.state.chain

    if not chain.unconfirmed_transactions:
        return {"status": "No transactions to mine"}

    if name not in get_all_miners():
        raise HTTPException(status_code=403, detail="Unauthorized miner")

    return {
        "status": "Block mined",
        "index": len(chain.chain) - 1,
        "transactions": chain.chain[-1].data
    }
