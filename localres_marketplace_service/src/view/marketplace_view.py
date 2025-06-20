from datetime import datetime

import logbook
from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPBearer

from localres_marketplace_service.src.blockchain.blockchain_manager import (
    BlockchainManager,
)
from localres_marketplace_service.src.blockchain.user import (
    UserViewModel as BlockchainUser,
)
from localres_marketplace_service.src.common.auth import async_admin_authorize
from localres_marketplace_service.src.common.models import GenericUser as GenericUser
from localres_marketplace_service.src.database.database_manager import DatabaseManager
from localres_marketplace_service.src.marketplace.core_logics import CoreLogics
from localres_marketplace_service.src.marketplace.data_types import (
    ConsumerData,
    ConsumerDataItem,
    ProsumerData,
    ProsumerDataItem,
)

logg = logbook.Logger(__name__)


marketplace_router = APIRouter()

@marketplace_router.get("/marketplace/database/run", tags=["marketplace"])
@async_admin_authorize
async def marketplace_database_run(request: Request, token=Depends(HTTPBearer())):
    core_logics: CoreLogics = request.app.state.core_logics
    database_manager: DatabaseManager = request.app.state.database_manager
    blockchain_manager: BlockchainManager = request.app.state.blockchain_manager
    consumer_data_item_list: list[ConsumerDataItem] = []
    prosumer_data_item_list: list[ProsumerDataItem] = []
    generic_users: list[GenericUser] = database_manager.get_users()
    blockchain_users: list[BlockchainUser] = blockchain_manager.get_user_value(
        "all").unwrap()
    timestamp: datetime = datetime.now()

    for generic_user in generic_users:
        blockchain_user = next(
            (blockchain_user for blockchain_user in blockchain_users if int(blockchain_user.user_id) ==
             generic_user.blockchain_id and generic_user.device is not None),
            None
        )
        if blockchain_user is None:
            logg.info(
                f"Generic user {generic_user.user_id} has no blockchain user")
            continue

        elif blockchain_user is not None:
                to_calc_hour = timestamp.hour - 1
                device = generic_user.device if generic_user.device is not None else ""
                threshold = blockchain_user.thresholds[to_calc_hour].value
            # CONSUMPTION
                logg.info(f"Getting consumption for device {device} at {timestamp}")
                consumption = database_manager.get_consumption_for_previous_hour(device=device, timestamp=timestamp)
                if len(consumption) == 0:
                    consumption = 0
                else:
                    consumption = consumption[0].value
                consumer_data_item = ConsumerDataItem(
                    id_consumer=generic_user.user_id,
                    threshold=threshold,
                    consumed_energy=consumption,
                    is_new=blockchain_user.is_new)
                consumer_data_item_list.append(consumer_data_item)
                # PRODUCTION
                production_device = generic_user.production_device
                if production_device is None:
                    logg.info(
                        f"Generic user {generic_user.user_id} has no production device")
                    continue
                logg.info(
                    f"Getting production for device {production_device} at {timestamp}")
                production = database_manager.get_production_for_previous_hour(device=production_device, timestamp=timestamp)
                if len(production) == 0:
                    production = 0
                else:
                    production = production[0].value
                prosumer_data_item = ProsumerDataItem(
                    id_prosumer=generic_user.user_id,
                    produced_energy=production
                )
                prosumer_data_item_list.append(prosumer_data_item) 
    consumer_data = ConsumerData(consumer_data=consumer_data_item_list)
    prosumer_data = ProsumerData(prosumer_data=prosumer_data_item_list)

    result = core_logics.apply_trading_logic(consumer_data, prosumer_data)
    if result.is_err:
        return result.unwrap_err()
    trading_data = result.unwrap()

    transactions = blockchain_manager.save_trading_data_to_algorand(
        trading_data, generic_users, blockchain_users
    )
    if transactions.is_err:
        return transactions.unwrap_err()
    tx_info_res = database_manager.insert_blockchain_data(
        transactions.unwrap()
    )
    if tx_info_res.is_err:
        return tx_info_res.unwrap_err()
    return "OK"


