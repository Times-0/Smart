from fastapi import Form
from typing import Optional
from pydantic import BaseModel


class Session(BaseModel):
    snfSession: Optional[str] = ""
    isMuted: Optional[bool] = False
    token:str
    worldName:str
    mpProduct:str
    data: Optional[int] = 0 # 0 for normal, 1 for tusk
    pid:str
    gameHeight:float


def SessionRequest(snfSession:str = Form(""),
    isMuted:bool = Form(False),
    token:str = Form(...),
    worldName:str = Form(...),
    mpProduct:str = Form(...),
    data:int = Form(0),
    pid:str = Form(...),
    gameHeight:float = Form(...)
) -> Session:
    
    return Session(
        snfSession = snfSession,
        isMuted = isMuted,
        token = token,
        worldName = worldName,
        mpProduct = mpProduct,
        data = data,
        pid = pid,
        gameHeight = gameHeight
    )