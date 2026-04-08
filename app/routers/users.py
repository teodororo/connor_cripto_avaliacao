from fastapi import APIRouter, Depends
from app.db import db
from app.core.security import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    return {"id": current_user.id, "name": current_user.name,
            "email": current_user.email, "balance": current_user.balance}

@router.get("/")
async def list_users(current_user=Depends(get_current_user)):
    users = await db.user.find_many()
    return [{"id": u.id, "name": u.name, "email": u.email} for u in users]
