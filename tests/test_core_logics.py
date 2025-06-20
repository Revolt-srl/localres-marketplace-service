import pytest
import logbook

from localres_marketplace_service.src.marketplace.core_logics import CoreLogics
from localres_marketplace_service.src.marketplace.data_types import (
    ConsumerData,
    ProsumerData,
    TradingData,
)

logger = logbook.Logger(__name__)


@pytest.mark.asyncio
async def test_core_logic_overproduction():
    logger.info("test_core_logic_overproduction")
    core_logics: CoreLogics = CoreLogics()
    # Consumer Data Overproduction
    consumer_data_overproduction = ConsumerData(
        consumer_data=[
            {
                "id_consumer": "C1",
                "threshold": 45,
                "consumed_energy": 8,
                "is_new": False,
            },
            {
                "id_consumer": "C3",
                "threshold": 25,
                "consumed_energy": 10,
                "is_new": False,
            },
            {
                "id_consumer": "C2",
                "threshold": 30,
                "consumed_energy": 6,
                "is_new": False,
            },
        ]
    )
    # Prosumer Data Overproduction
    prosumer_data_overproduction = ProsumerData(
        prosumer_data=[
            {"id_prosumer": "P1", "produced_energy": 20},
            {"id_prosumer": "P2", "produced_energy": 25},
        ]
    )
    # Trading Data OverProduction Result
    trading_data_overproduction = TradingData(
        trading_data=[
            {
                "id_consumer": "C1",
                "trades": [
                    {
                        "id_prosumer": "P1",
                        "given_T": 157.5,
                        "purchased_energy": 3.5,
                        "received_T": 192.5,
                    },
                    {
                        "id_prosumer": "P2",
                        "given_T": 202.5,
                        "purchased_energy": 4.5,
                        "received_T": 247.5,
                    },
                ],
            },
            {
                "id_consumer": "C2",
                "trades": [
                    {
                        "id_prosumer": "P1",
                        "given_T": 78.0,
                        "purchased_energy": 2.6,
                        "received_T": 182.0,
                    },
                    {
                        "id_prosumer": "P2",
                        "given_T": 102.0,
                        "purchased_energy": 3.4,
                        "received_T": 238.0,
                    },
                ],
            },
            {
                "id_consumer": "C3",
                "trades": [
                    {
                        "id_prosumer": "P1",
                        "given_T": 110.0,
                        "purchased_energy": 4.4,
                        "received_T": 330.0,
                    },
                    {
                        "id_prosumer": "P2",
                        "given_T": 140.0,
                        "purchased_energy": 5.6,
                        "received_T": 420.0,
                    },
                ],
            },
        ]
    )

    result = core_logics.apply_trading_logic(
        consumer_data_overproduction, prosumer_data_overproduction
    )
    assert result.is_ok
    assert result.unwrap() == trading_data_overproduction


@pytest.mark.asyncio
async def test_core_logic_underproduction():
    logger.info("test_core_logic_underproduction")
    core_logics: CoreLogics = CoreLogics()
    # Consumer Data Underproduction
    consumer_data_underproduction = ConsumerData(
        consumer_data=[
            {
                "id_consumer": "C1",
                "threshold": 55,
                "consumed_energy": 10,
                "is_new": False,
            },
            {
                "id_consumer": "C2",
                "threshold": 70,
                "consumed_energy": 8,
                "is_new": False,
            },
            {
                "id_consumer": "C3",
                "threshold": 75,
                "consumed_energy": 12,
                "is_new": False,
            },
        ]
    )
    # Prosumer Data Underproduction
    prosumer_data_underproduction = ProsumerData(
        prosumer_data=[
            {"id_prosumer": "P1", "produced_energy": 10},
            {"id_prosumer": "P2", "produced_energy": 8},
        ]
    )
    # Trading Data Underproduction
    trading_data_underproduction = TradingData(
        trading_data=[
            {
                "id_consumer": "C3",
                "trades": [
                    {
                        "id_prosumer": "P1",
                        "given_T": 502.5,
                        "purchased_energy": 6.7,
                        "received_T": 167.5,
                    },
                    {
                        "id_prosumer": "P2",
                        "given_T": 397.5,
                        "purchased_energy": 5.3,
                        "received_T": 132.5,
                    },
                ],
            },
            {
                "id_consumer": "C2",
                "trades": [
                    {
                        "id_prosumer": "P1",
                        "given_T": 231.0,
                        "purchased_energy": 3.3,
                        "received_T": 99.0,
                    },
                    {
                        "id_prosumer": "P2",
                        "given_T": 189.0,
                        "purchased_energy": 2.7,
                        "received_T": 81.0,
                    },
                ],
            },
            {
                "id_consumer": "C1",
                "trades": [
                    {
                        "id_prosumer": "P1",
                        "given_T": 0,
                        "purchased_energy": 0,
                        "received_T": 0,
                    },
                    {
                        "id_prosumer": "P2",
                        "given_T": 0,
                        "purchased_energy": 0,
                        "received_T": 0,
                    },
                ],
            },
        ]
    )

    result = core_logics.apply_trading_logic(
        consumer_data_underproduction, prosumer_data_underproduction
    )
    assert result.is_ok
    assert result.unwrap() == trading_data_underproduction


@pytest.mark.asyncio
async def test_core_logic_skip_iteration():
    logger.info("test_skip_iteration")
    core_logics: CoreLogics = CoreLogics()
    # Consumer Data Overproduction
    consumer_data_overproduction = ConsumerData(
        consumer_data=[
            {
                "id_consumer": "C1",
                "threshold": 45,
                "consumed_energy": 8,
                "is_new": False,
            },
            {
                "id_consumer": "C3",
                "threshold": 25,
                "consumed_energy": 10,
                "is_new": False,
            },
            {
                "id_consumer": "C2",
                "threshold": 30,
                "consumed_energy": 6,
                "is_new": False,
            },
        ]
    )
    # Prosumer Data Overproduction
    prosumer_data_overproduction = ProsumerData(
        prosumer_data=[
            {"id_prosumer": "C1", "produced_energy": 20},
            {"id_prosumer": "P2", "produced_energy": 25},
        ]
    )
    result = core_logics.apply_trading_logic(
        consumer_data_overproduction, prosumer_data_overproduction
    )
    assert result.is_ok
    result = result.unwrap()
    assert len(result.trading_data[0]["trades"]) == 1
    assert len(result.trading_data[1]["trades"]) == 2
    assert len(result.trading_data[2]["trades"]) == 2
