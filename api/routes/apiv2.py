from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import PlainTextResponse

from api.models.request.Session import SessionRequest, Session
from api.models.response import DefaultResponse, ErrorData

from typing import Any, Dict, Type
import bcrypt
import os
import asyncio
import json

router = APIRouter()
#[WNS]/api/v0.2/xxx/game/get/world-name-service/start_world_request?name=[$worldname]&token=[SNFSESSION]&nuCache=[$nuCache]&product_name=[$productname]&owner=[$owner]


async def authenticate_session(request: Request, name:str, token:str, owner:str, product_name:str = 'cjsnow') -> Session:
    redis = request.app.state.redis

    session_json_dump = await redis.get(f"session:{token}")
    if session_json_dump is None:
        return None

    sessionObj = Session.parse_raw(session_json_dump)

    if sessionObj.worldName != name or sessionObj.pid != owner or product_name != sessionObj.mpProduct:
        sessionObj.mpProduct = sessionObj.worldName = sessionObj.pid = None

    return sessionObj


@router.get("/get/world-name-service/start_world_request", response_class=PlainTextResponse)
async def authenticate_and_generate_session(request: Request, session:Session = Depends(authenticate_session)) -> str:
    try:
        if session is None:
            return "[S_ERROR]|3104|Smart Error|-1|slave does not exist"

        elif session.worldName is None or session.pid is None:
            return "[S_ERROR]|3104|Smart Error|-1|invalid token"

        redis = request.app.state.redis

        cjservers = await redis.smembers("cjs_servers", encoding='utf-8')
        available_server = None
        for server in cjservers:
            server_data = await redis.hgetall(f"cj_server:{server}", encoding='utf-8')

            if server_data['users'] < server_data['max']:
                available_server = server_data
                break

        else:
            return "[S_ERROR]|3902|Smart Error|-1|no available servers"

        return f"[S_WORLDLIST]|{available['id']}|Smart|{available['ip']}|{available['port']}|Dote|Bale|{available['name']}|TimelineSmartServer"

    except Exception as e:
        return "[S_ERROR]|3104|Smart Error|-1|{e}"

