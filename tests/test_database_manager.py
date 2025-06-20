import datetime
import pytest
import logbook

from localres_marketplace_service.src.common.models import TransactionWriteModel
from localres_marketplace_service.src.database.database_manager import DatabaseManager

logger = logbook.Logger(__name__)


@pytest.mark.asyncio
async def test_database_manager_insert_trading_data():
    logger.info("Testing DatabaseManager")
    db_manager = DatabaseManager.from_env()
    
    # Test getting a session
    session = db_manager.get_session()
    assert session is not None, "Session should not be None"
    
    transaction_write_model_list = [
        TransactionWriteModel(
            prosumer_id="P1",
            consumer_id="C1",
            id_transaction="T1",
            given_T=100.0,
            purchased_energy=10.0,
            received_T=90.0
        ),
        TransactionWriteModel(
            prosumer_id="P2",
            consumer_id="C2",
            id_transaction="T2",
            given_T=200.0,
            purchased_energy=20.0,
            received_T=180.0
        )
    ]

    result = db_manager.insert_blockchain_data(transaction_write_model_list)
    assert result.is_ok, "Trading data should be inserted successfully"
    result = result.unwrap()
    assert result is None, "Result should be None after successful insertion"

    # Test closing the session
    db_manager.close_session(session)
    
    # Test disposing the engine
    db_manager.dispose_engine()

@pytest.mark.asyncio
async def test_database_manager_get_consumption():
    logger.info("Testing DatabaseManager")
    db_manager = DatabaseManager.from_env()
    
    # Test getting a session
    session = db_manager.get_session()
    assert session is not None, "Session should not be None"
    
    # Test getting consumption data
    timestamp: datetime.datetime = datetime.datetime(2025, 6, 12, 17, 0, 0)
    consumption_data = db_manager.get_consumption_for_previous_hour(device="device_c1", timestamp=timestamp)
    assert isinstance(consumption_data, list), "Consumption data should be a list"
    
    assert len(consumption_data) > 0

    if consumption_data:
        assert hasattr(consumption_data[0], 'device'), "Consumption data should have device attribute"
        assert hasattr(consumption_data[0], 'timestamp'), "Consumption data should have timestamp attribute"
        assert hasattr(consumption_data[0], 'value'), "Consumption data should have value attribute"

@pytest.mark.asyncio
async def test_database_manager_get_production():
    logger.info("Testing DatabaseManager")
    db_manager = DatabaseManager.from_env()
    
    # Test getting a session
    session = db_manager.get_session()
    assert session is not None, "Session should not be None"
    
    # Test getting production data
    timestamp: datetime.datetime = datetime.datetime(2025, 6, 12, 17, 0, 0)
    production_data = db_manager.get_production_for_previous_hour(device="device_p1", timestamp=timestamp)
    assert isinstance(production_data, list), "Production data should be a list"
    
    assert len(production_data) > 0

    if production_data:
        assert hasattr(production_data[0], 'device'), "Production data should have device attribute"
        assert hasattr(production_data[0], 'timestamp'), "Production data should have timestamp attribute"
        assert hasattr(production_data[0], 'value'), "Production data should have value attribute"


@pytest.mark.asyncio
async def test_database_manager_get_users():
    logger.info("Testing DatabaseManager")
    db_manager = DatabaseManager.from_env()
    
    # Test getting a session
    session = db_manager.get_session()
    assert session is not None, "Session should not be None"
    
    # Test closing the session
    db_manager.close_session(session)
    
    # Test disposing the engine
    db_manager.dispose_engine()
    
    # Test getting users
    users = db_manager.get_users()
    assert isinstance(users, list), "Users should be a list"
    
    if users:
        assert hasattr(users[0], 'user_id'), "User should have user_id attribute"
        assert hasattr(users[0], 'device'), "User should have device attribute"
        assert hasattr(users[0], 'blockchain_id'), "User should have blockchain_id attribute"