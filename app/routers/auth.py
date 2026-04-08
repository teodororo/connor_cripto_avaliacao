from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from app.core.security import create_token, hash_password, verify_password
from app.db import db

router = APIRouter(prefix="/auth", tags=["Auth"])

class RegisterIn(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

@router.post("/register", status_code=201)
async def register(body: RegisterIn):
    print(f"DEBUG: Tipo da senha: {type(body.password)}")
    print(f"DEBUG: Conteúdo da senha: {body.password}")
    existing = await db.user.find_unique(where={"email": body.email})
    if existing:
        raise HTTPException(400, "Email already registered")
    user = await db.user.create(data={
        "name": body.name,
        "email": body.email,
        "password": hash_password(body.password),
    })
    return {"id": user.id, "email": user.email}


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # o Swagger envia o e-mail no campo chamado 'username'
    user = await db.user.find_unique(where={"email": form_data.username})

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(401, "Invalid credentials")

    token = create_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}
