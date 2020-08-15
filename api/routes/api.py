from fastapi import APIRouter

from api.routes import snfgenerator

router = APIRouter()
router.include_router(snfgenerator.router, tags=["SNFGenerator"], prefix="/snfgenerator")