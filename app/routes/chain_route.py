from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/chain", tags=["Blockchain"], summary="Get the blockchain")
def get_chain(request: Request):
    chain = request.app.state.chain
    return chain.to_dict()