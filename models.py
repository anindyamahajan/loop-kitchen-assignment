from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class StorePollData(Base):
    __tablename__ = 'store_poll_data'
    id = Column(Integer, primary_key=True)
    store_id = Column(String)
    status = Column(String)
    timestamp_utc = Column(DateTime)


class StoreBusinessHours(Base):
    __tablename__ = 'store_business_hours'
    id = Column(Integer, primary_key=True)
    store_id = Column(String)
    day_of_week = Column(Integer)
    start_time_local = Column(String)
    end_time_local = Column(String)


class StoreTimezone(Base):
    __tablename__ = 'store_timezone'
    id = Column(Integer, primary_key=True)
    store_id = Column(String)
    timezone = Column(String)


class Reports(Base):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True)
    report_id = Column(String)
