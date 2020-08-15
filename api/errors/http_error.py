from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse


async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:

    if isinstance(exc.detail, str):
        return JSONResponse(
        {
            "hasError": True,
            "success": False,
            "data": {
                "error_msg": exc.detail
            }
        }, 
        status_code=exc.status_code
    )

    return JSONResponse(
        {
            "hasError": True,
            "success": False,
            "data": {
                "errors": [exc.detail]
            }
        }, 
        status_code=exc.status_code
    )