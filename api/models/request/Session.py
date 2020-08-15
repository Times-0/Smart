from typing import Optional
from pydantic import BaseModel


class SessionRequest(BaseModel):
    snfSession: Optional[str] = ""
    isMuted: Optional[bool] = False
    token:str
    worldName:str
    mpProduct:str
    data: Optional[int] = 0 # 0 for normal, 1 for tusk
    pid:str
    gameHeight:float

