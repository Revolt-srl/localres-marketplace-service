import os
from datetime import datetime
from typing import Self

from option import Err, Ok, Result
from pydantic import BaseModel
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from localres_marketplace_service.src.common.models import (
    Consumption,
    GenericUser,
    Production,
    TransactionWriteModel,
)
from localres_marketplace_service.src.common.orm import (
    Consumption as DatabaseConsumption,
)
from localres_marketplace_service.src.common.orm import Production as DatabaseProduction
from localres_marketplace_service.src.common.orm import (
    TradingData as DatabaseTradingData,
)
from localres_marketplace_service.src.common.orm import User as DatabaseUser


class DatabaseManager(BaseModel):
    """
    DatabaseManager is responsible for managing the database connection and operations.
    It provides methods to connect to the database, execute queries, and handle transactions.
    """

    class Config:
        arbitrary_types_allowed = True

    engine: Engine

    @classmethod
    def from_env(cls) -> Self:
        """ Create a DatabaseManager instance using the connection string from environment variables.
        Raises:
            ValueError: If the connection string is not set in the environment variables.
        """
        user = os.getenv("SOURCE_POSTGRES_USER")
        if not user:
            raise ValueError("Database user must be set in environment variables.")
        password = os.getenv("SOURCE_POSTGRES_PASSWORD")
        if not password:
            raise ValueError("Database password must be set in environment variables.")
        host = os.getenv("SOURCE_POSTGRES_HOST")
        if not host:
            raise ValueError("Database host must be set in environment variables.")
        port = os.getenv("SOURCE_POSTGRES_PORT")
        if not port:
            raise ValueError("Database port must be set in environment variables.")
        database = os.getenv("SOURCE_POSTGRES_DBNAME")
        if not database:
            raise ValueError("Database name must be set in environment variables.")
        
        connection_string = f"postgresql+pg8000://{user}:{password}@{host}:{port}/{database}"

        engine = create_engine(connection_string, client_encoding="utf8", poolclass=NullPool)
        return cls(engine=engine)
    
    def get_session(self) -> Session:
        """
        Get a new session from the engine.
        """
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        return SessionLocal()
    
    def close_session(self, session: Session) -> None:
        """
        Close the given session.
        """
        session.close()
    
    def dispose_engine(self) -> None:
        """
        Dispose of the engine.
        """
        self.engine.dispose()
    
    def get_engine(self) -> Engine:
        """
        Get the SQLAlchemy engine.
        """
        return self.engine
    
    def get_production_for_previous_hour(self, device: str, timestamp: datetime) -> list[Production]:
        """
        Retrieve production data for a specific device and for the previous hour.
        Args:
            device (str): The device identifier.
            timestamp (str): The timestamp in ISO format.

        Returns:
            list[Production]: A list of Production objects.

        """
        timestamp_to_calculate = timestamp.replace(hour=timestamp.hour-1)
        timestamp_one_hour_before = timestamp.replace(hour=timestamp.hour-2)

        with self.get_session() as session:
            productions = session.query(DatabaseProduction).filter(
                DatabaseProduction.device == device,
                DatabaseProduction.timestamp >= timestamp_one_hour_before,
                DatabaseProduction.timestamp < timestamp_to_calculate
            ).all()
            return [Production(
                device=production.device,
                timestamp=production.timestamp.isoformat(),
                value=production.value
            ) for production in productions]
    
    def get_consumption_for_previous_hour(self, device: str, timestamp: datetime) -> list[Consumption]:
        """
        Retrieve consumption data for a specific device and for the previous hour.
        Args:
            device (str): The device identifier.
            timestamp (str): The timestamp in ISO format.

        Returns:
            list[Consumption]: A list of Consumption objects.

        """
        timestamp_to_calculate = timestamp.replace(hour=timestamp.hour-1)
        timestamp_one_hour_before = timestamp.replace(hour=timestamp.hour-2)

        with self.get_session() as session:
            consumptions = session.query(DatabaseConsumption).filter(
                DatabaseConsumption.device == device,
                DatabaseConsumption.timestamp >= timestamp_one_hour_before,
                DatabaseConsumption.timestamp < timestamp_to_calculate
            ).all()
            return [Consumption(
                device=consumption.device,
                timestamp=consumption.timestamp.isoformat(),
                value=consumption.value
            ) for consumption in consumptions]

    def get_users(self) -> list[GenericUser]:
        """
        Retrieve all users from the database.
        Returns:
            list[DatabaseUser]: A list of DatabaseUser objects.

        """
        with self.get_session() as session:
            users = session.query(DatabaseUser).all()
            return [GenericUser(
                user_id=user.id,
                device=user.device,
                threshold=None,  # Assuming threshold is not stored in User model
                blockchain_id=user.blockchain_id,
                production_device=user.production_device
            ) for user in users]

    def insert_blockchain_data(self, input: list[TransactionWriteModel]) -> Result[None, Exception]:
        try:
            for transaction in input:
                with self.get_session() as session:
                    db_trading_data= DatabaseTradingData(
                        timestamp=datetime.now().isoformat(),
                        value=transaction.given_T,
                        consumer_id=transaction.consumer_id,
                        prosumer_id=transaction.prosumer_id,
                        transaction_id=transaction.id_transaction,
                        purchased_energy=transaction.purchased_energy,
                        prosumer_value=transaction.received_T
                    )
                    session.add(db_trading_data)
                    session.commit()
            return Ok(None)
        except Exception as e:
            return Err(e)