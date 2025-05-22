from fastapi import APIRouter, Request, HTTPException

router = APIRouter()

@router.get("/mine", tags=["Blockchain"], summary="Mine a new block")
def mine(name: str, request: Request):
    chain = request.app.state.chain

    if not chain.unconfirmed_transactions:
        return {"status": "No transactions to mine"}

    # Check if miner is authorized
    from database import get_all_miners
    if name not in get_all_miners():
        raise HTTPException(status_code=403, detail="Unauthorized miner")

    proof = chain.mine()

    return {
        "status": "Block mined",
        "index": len(chain.chain) - 1,
        "transactions": chain.chain[-1].data
    }
