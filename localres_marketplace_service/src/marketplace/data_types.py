from typing import List
from pydantic import BaseModel, NonNegativeFloat
from typing_extensions import TypedDict


class ConsumerDataItem(TypedDict):
    id_consumer: str
    threshold: NonNegativeFloat
    consumed_energy: NonNegativeFloat
    is_new: bool


class ConsumerData(BaseModel):
    consumer_data: List[ConsumerDataItem]


class ProsumerDataItem(TypedDict):
    id_prosumer: str
    produced_energy: NonNegativeFloat


class ProsumerData(BaseModel):
    prosumer_data: List[ProsumerDataItem]


class InternalTradesData(TypedDict):
    id_prosumer: str
    given_T: NonNegativeFloat
    purchased_energy: NonNegativeFloat
    received_T: NonNegativeFloat


class ConsumerTradingData(TypedDict):
    id_consumer: str
    trades: List[InternalTradesData]


class TradingData(BaseModel):
    trading_data: List[ConsumerTradingData]
