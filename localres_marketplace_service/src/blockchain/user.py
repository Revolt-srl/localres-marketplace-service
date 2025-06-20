from pydantic import BaseModel

class User(BaseModel):
    user_id: str
    balance: int
    thresholds: list[str]
    is_new: bool

    class Config:
        arbitrary_types_allowed = True

    def to_view_model(self):
        thresholds = []
        h: int = 0
        for threshold in self.thresholds:
            thresholds.append(Threshold(
                hour=h,
                value=int(threshold)
            ))
            h += 1
        return UserViewModel(
            user_id=self.user_id,
            balance=self.balance,
            thresholds=thresholds,
            is_new=self.is_new
        )


class Threshold(BaseModel):
    hour: int
    value: int

    class Config:
        arbitrary_types_allowed = True


class UserViewModel(BaseModel):
    user_id: str
    balance: int
    thresholds: list[Threshold]
    is_new: bool = True

    class Config:
        arbitrary_types_allowed = True

    def to_write_model(self):
        ts_value: bytes = b"ps_"
        user_id: bytes = self.user_id.encode('utf-8')
        ts_string = ''.join(
            f"{threshold.value:03}" for threshold in self.thresholds)
        user_value: bytes = ts_value + ts_string.encode('utf-8') + b"balance_" + \
            self.balance.to_bytes(8, "big")
        return UserWriteModel(
            user_id=user_id,
            user_value=user_value
        )


class UserWriteModel(BaseModel):
    user_id: bytes
    user_value: bytes

    class Config:
        arbitrary_types_allowed = True
