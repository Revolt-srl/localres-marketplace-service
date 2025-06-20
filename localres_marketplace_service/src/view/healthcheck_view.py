from fastapi import APIRouter
from fastapi.responses import RedirectResponse

health_router = APIRouter()


@health_router.get("/", tags=["utilities"])
async def docs():
    return RedirectResponse(url="/docs")


@health_router.get("/healthcheck", tags=["utilities"])
async def health():
    return "OK"
