import os
import sys
from fastapi.concurrency import asynccontextmanager
import logbook
from fastapi import FastAPI
from localres_marketplace_service.src.view.healthcheck_view import health_router
from localres_marketplace_service.src.view.blockchain_view import blockchain_router
from localres_marketplace_service.src.view.marketplace_view import marketplace_router

from localres_marketplace_service.src.configuration import configure_marketplace_endpoint_service

logbook.StreamHandler(
    sys.stdout, level=logbook.DEBUG if os.environ.get(
        "DEBUG") else logbook.INFO
).push_application()
logg = logbook.Logger("Localres Marketplace Service")
logg.info("Starting application")
logg.debug("THIS IS RUNNING IN DEBUG MODE")


@asynccontextmanager
async def lifespan(app):
    await configure_marketplace_endpoint_service(app)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(health_router)
app.include_router(blockchain_router)
app.include_router(marketplace_router)
