from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from ratelimit import RateLimitMiddleware, Rule
from ratelimit.auths import EmptyInformation
from ratelimit.backends.redis import RedisBackend
from ratelimit.auths.ip import client_ip
from ratelimit.auths.session import from_session

from api.errors.http_error import http_error_handler
from api.errors.validation_error import http422_error_handler
from api.routes.api import router as api_router
from api.routes.api import router_rate_limits
from api.core.config import ALLOWED_HOSTS, API_PREFIX, DEBUG, SECRET_KEY
from api.core.events import create_start_app_handler, create_stop_app_handler


async def AUTH_FUNCTION(scope):
    return scope['client'][0], "default" #USER_UNIQUE_ID, GROUP_NAME


def get_application() -> FastAPI:
    application = FastAPI(
        debug = True,
        title = "Smart Server",
        description = "MP session and game handler",
        version = "0.0.1",
        docs_url = "/api/docs",
        redoc_url = "/api/redocs"
    )
    
    application.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_HOSTS or ["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    application.add_middleware(
        SessionMiddleware,
        secret_key=SECRET_KEY,
        same_site='None'
    )

    '''
    Note: If the API is a proxy to base play url (eg: play.localhost/cjs/...), it's better to use from_session
          else, for generic purpose, you can rate limit using IP address too.
    '''
    #AUTH_FUNCTION = client_ip or from_session
    application.add_middleware(
        RateLimitMiddleware,
        authenticate=AUTH_FUNCTION,
        backend=RedisBackend(),
        config=router_rate_limits
        #{
        #    r"^/second_limit": [Rule(second=1), Rule(group="admin")],
        #    r"^/minute_limit": [Rule(minute=1), Rule(group="admin")],
        #},
    )

    application.add_event_handler("startup", create_start_app_handler(application))
    application.add_event_handler("shutdown", create_stop_app_handler(application))

    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(RequestValidationError, http422_error_handler)

    application.include_router(api_router)

    return application


app = get_application()
