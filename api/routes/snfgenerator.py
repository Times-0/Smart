from fastapi import APIRouter, Body, Depends, HTTPException, Request

from api.models.request.Session import SessionRequest
from api.models.response import DefaultResponse, ErrorData

router = APIRouter()

responses = {
    403: {
        "model": DefaultResponse[ErrorData], 
        "message": "Failed to authenticate token"
    }
}


async def authenticate_session(request: Request, session:SessionRequest) -> str:
    return ""


@router.post("/session", tags=["MP_Session"], response_model=DefaultResponse, response_model_exclude_unset=True, responses=responses)
async def authenticate_and_generate_session(snfSession:str = Depends(authenticate_session)) -> DefaultResponse:
    pass

