from fastapi import APIRouter
from ratelimit import Rule

from api.routes import snfgenerator

router_rate_limits = {
    r'^/snfgenerator/': [Rule(second=1)],
    r'^/api/v0.2/xxx/game/': [Rule(second=1)]
}

router = APIRouter()
router.include_router(snfgenerator.router, tags=["SNFGenerator"], prefix="/snfgenerator")
#router.include_router(apiv2.router, tags="API v2.0", prefix="/api/v0.2/xxx/game/")
