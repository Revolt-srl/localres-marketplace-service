from typing import Optional
from pydantic import BaseModel

class Consumption(BaseModel):
    device: str
    timestamp: str
    value: float

    class Config:
        arbitrary_types_allowed = True

class Production(BaseModel):
    device: str
    timestamp: str
    value: float

    class Config:
        arbitrary_types_allowed = True

class GenericUser(BaseModel):
    user_id: str
    device: Optional[str]
    threshold: Optional[float]
    blockchain_id: Optional[int]
    production_device: Optional[str]

    class Config:
        arbitrary_types_allowed = True


class TransactionWriteModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    prosumer_id: str
    consumer_id: str
    id_transaction: str
    purchased_energy: float
    given_T: float
    received_T: float
