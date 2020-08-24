from fastapi import APIRouter, Response
from fastapi.responses import PlainTextResponse
from ratelimit import Rule

from api.routes import snfgenerator, apiv2

router_rate_limits = {
    r'^/snfgenerator/': [Rule(second=1)],
    r'^/api/v0.2/xxx/game/': [Rule(second=0.2)]
}

router = APIRouter()
router.include_router(snfgenerator.router, tags=["SNFGenerator"], prefix="/snfgenerator")
router.include_router(apiv2.router, tags=["API v2.0"], prefix="/api/v0.2/xxx/game")


@router.get("/crossdomain.xml")
@router.get("/{path:path}/crossdomain.xml")
def get_cross_domain(path=None):
    return Response(
        content='<cross-domain-policy><allow-access-from domain="*"/></cross-domain-policy>', 
        media_type="application/xml"
    )

@router.get("/api/ping", response_class=PlainTextResponse)
def ping():
    return "[S_PING]|Smart|Pong"