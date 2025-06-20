from sqlalchemy import Column, Float, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TradingData(Base):
    __tablename__ = 'trading_data'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False)
    value = Column(Float, nullable=False)
    consumer_id = Column(String, index=True)
    prosumer_id = Column(String, index=True)
    purchased_energy = Column(Float, nullable=False)
    prosumer_value = Column(Float, nullable=False)
    transaction_id = Column(String)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True, index=True)
    device = Column(String, unique=True, index=True)
    blockchain_id = Column(Integer, unique=True, index=True)
    production_device = Column(String, nullable=True)
    
class Production(Base):
    __tablename__ = 'production'
    
    id = Column(String, primary_key=True, index=True)
    device = Column(String)
    timestamp = Column(DateTime, nullable=False)
    value = Column(Float, nullable=False)
    
class Consumption(Base):
    __tablename__ = 'consumption'
    
    id = Column(String, primary_key=True, index=True)
    device = Column(String)
    timestamp = Column(DateTime, nullable=False)
    value = Column(Float, nullable=False)
    