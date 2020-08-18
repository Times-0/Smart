from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder

from api.models.request.Session import SessionRequest, Session
from api.models.response import DefaultResponse, ErrorData

from typing import Any, Dict, Type
import bcrypt
import os
import asyncio
import json

router = APIRouter()

responses = {
    403: {
        "model": DefaultResponse[ErrorData[dict]], 
        "message": "Failed to authenticate token"
    }
}


async def authenticate_session(request: Request, session:Session = Depends(SessionRequest)) -> Session:
    redis = request.app.state.redis
    loop = asyncio.get_event_loop()

    mp_session_key = await redis.get(f"mp_session:{session.pid}")
    if mp_session_key is None:
        raise HTTPException(status_code=403, detail="Token key doesn't exist or expired")

    key_match = await loop.run_in_executor(None, bcrypt.checkpw, mp_session_key, session.token.encode())
    if not key_match:
        raise HTTPException(status_code=403, detail="Invalid token key")

    session.snfSession = os.urandom(10).hex()
    return session


@router.post("/session", response_model=DefaultResponse[str], response_model_exclude_unset=True, responses=responses)
async def authenticate_and_generate_session(request: Request, session:Session = Depends(authenticate_session)) -> DefaultResponse[str]:
    request.session['user'] = session.pid
    request.session['group'] = "default"

    redis = request.app.state.redis
    loop = asyncio.get_event_loop()

    await redis.set(f"session:{session.snfSession}", json.dumps(jsonable_encoder(session)))
    await redis.delete(f"mp_session:{session.pid}")

    return DefaultResponse[str](
        hasError = True,
        success = True,
        data = session.snfSession
    )


def dummy(func):
    print(func, func.__dict__, dir(func))

    return lambda *x: None

@dummy
@router.get("/test")
async def test(request: Request):
    print(request.session)
    return f"user={request.session['user']}"