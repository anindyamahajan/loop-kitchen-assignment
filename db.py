from contextlib import contextmanager
from datetime import timedelta

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from db_helpers import process_business_hours, process_store_poll_data
from load_data import load_all_data
from models import StorePollData, StoreTimezone, StoreBusinessHours, Reports

load_all_data()

DATABASE_URL = 'sqlite:///./base.db'

# Create SQLite database engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fetch the maximum timestamp value from store_poll_data table and set as global constant
with engine.connect() as conn:
    MAX_TIMESTAMP = NOW = conn.execute(func.max(StorePollData.timestamp_utc)).scalar()


@contextmanager
def get_db():
    try:
        db = SessionLocal()
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()


def get_all_store_ids():
    with get_db() as db:
        # Execute query to fetch all distinct store_id values from store_poll_data table
        query = db.query(StorePollData.store_id).distinct().all()
        # Extract store_ids from query result and return as list
        store_ids = [result[0] for result in query]
        return store_ids


def get_store_timezone(store_id):
    with get_db() as db:
        # Query store_timezone table to get the store's timezone
        store_timezone = db.query(StoreTimezone.timezone).filter(StoreTimezone.store_id == store_id).first()
        if store_timezone is None:
            # If store's timezone is not found, assume it is America/Chicago
            store_timezone = ('America/Chicago',)

        return store_timezone[0]


def get_store_poll_data(store_id):
    with get_db() as db:
        # Calculate the date 7 days ago from the current date
        date_7_days_ago = NOW - timedelta(days=7)
        # Execute query to fetch data from store_poll_data table
        query_result = db.query(StorePollData).filter(StorePollData.timestamp_utc >= date_7_days_ago,
                                                      StorePollData.store_id == store_id).order_by(
            StorePollData.timestamp_utc.asc()).all()
        return process_store_poll_data(query_result, get_store_timezone(store_id))


def get_store_business_hours(store_id: str):
    with get_db() as db:
        # Query store_business_hours table to get all rows for the store_id
        store_business_hours = db.query(StoreBusinessHours).filter(StoreBusinessHours.store_id == store_id).all()
        return process_business_hours(store_business_hours, get_store_timezone(store_id), NOW)


def store_report_id(report_id: str):
    with get_db() as db:
        # Insert report_id into reports table
        db.add(Reports(report_id=report_id))


def report_id_exists(report_id: str):
    with get_db() as db:
        # Query reports table to check if the report_id exists
        exists = db.query(Reports).filter(Reports.report_id == report_id).first()
        return True if exists else False
