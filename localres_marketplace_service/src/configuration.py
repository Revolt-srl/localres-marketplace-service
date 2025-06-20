import logbook
from fastapi import FastAPI

from localres_marketplace_service.src.blockchain.blockchain_manager import (
    BlockchainManager,
)
from localres_marketplace_service.src.database.database_manager import DatabaseManager
from localres_marketplace_service.src.marketplace.core_logics import CoreLogics

logg = logbook.Logger(__name__)


async def configure_marketplace_endpoint_service(app: FastAPI) -> None:
    bm: BlockchainManager = BlockchainManager.from_env()
    cl: CoreLogics = CoreLogics()
    dbm: DatabaseManager = DatabaseManager.from_env()

    app.state.blockchain_manager = bm
    app.state.core_logics = cl
    app.state.database_manager = dbm

    logg.info("ADDED LOCALRES OBJECTS TO APP STATE DICT")
