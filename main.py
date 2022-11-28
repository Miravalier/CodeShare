from __future__ import annotations

import secrets
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from security import check_password, hash_password
from database import db
from utils import random_id
from models import User


app = FastAPI()


class JsonError(Exception):
    pass


@app.exception_handler(JsonError)
async def auth_error_handler(request: Request, exc: JsonError):
    return JSONResponse(status_code=401, content={
        "status": "error",
        "reason": str(exc)
    })


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/api/login")
async def login(request: LoginRequest):
    # Find the requested user by username
    user: Optional[User] = db.users_by_name[request.username]
    if not user:
        raise JsonError("invalid username or password")

    # Check the password
    if not check_password(request.password, user.hashed_password):
        raise JsonError("invalid username or password")

    # Generate a token and create a session
    token = secrets.token_hex(16)
    db.users_by_token[token] = user
    return {"status": "success", "token": token}


class RegisterRequest(BaseModel):
    username: str
    password: str


@app.post("/api/register")
async def user_create(request: RegisterRequest):
    # Get user struct
    user = db.users[request.username]
    if user:
        raise JsonError("username taken")
    # Create new user
    user = User(id=random_id(), name=request.username, hashed_password=hash_password(request.password))
    db.users[user.id] = user
    db.users_by_name[user.name] = user
    # Return success
    return {"status": "success", "id": user.id}


@app.on_event("shutdown")
async def shutdown():
    print("Saving database ...")
    db.save()