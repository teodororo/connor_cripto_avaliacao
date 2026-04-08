from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.security import generate_nonce, get_current_user
from app.db import db

router = APIRouter(prefix="/transactions", tags=["Transactions"])

class TransferIn(BaseModel):
    receiver_id: int
    amount: float
    nonce: str  # client-generated unique value — prevents replay attacks

@router.post("/transfer", status_code=201)
async def transfer(body: TransferIn, current_user=Depends(get_current_user)):
    if body.amount <= 0:
        raise HTTPException(400, "Amount must be positive")
    if body.receiver_id == current_user.id:
        raise HTTPException(400, "Cannot transfer to yourself")

    # Replay attack prevention: nonce must be globally unique
    existing = await db.transaction.find_unique(where={"nonce": body.nonce})
    if existing:
        raise HTTPException(409, "Duplicate transaction (replay detected)")

    if current_user.balance < body.amount:
        raise HTTPException(422, "Insufficient funds")

    receiver = await db.user.find_unique(where={"id": body.receiver_id})
    if not receiver:
        raise HTTPException(404, "Receiver not found")

    # Atomic balance update + transaction record
    await db.user.update(where={"id": current_user.id},
                         data={"balance": {"decrement": body.amount}})
    await db.user.update(where={"id": receiver.id},
                         data={"balance": {"increment": body.amount}})
    tx = await db.transaction.create(data={
        "senderId": current_user.id,
        "receiverId": receiver.id,
        "amount": body.amount,
        "nonce": body.nonce,
    })
    return {"transaction_id": tx.id, "amount": tx.amount, "nonce": tx.nonce}

@router.get("/nonce")
async def get_nonce(current_user=Depends(get_current_user)):
    """Helper: server generates a fresh nonce for the client to use."""
    return {"nonce": generate_nonce()}

@router.get("/history")
async def history(current_user=Depends(get_current_user)):
    txs = await db.transaction.find_many(
        where={
            "OR": [
                {"senderId": current_user.id},
                {"receiverId": current_user.id}
            ]
        },
        include={
            "sender": False,
            "receiver": False
        }
    )
    return txs