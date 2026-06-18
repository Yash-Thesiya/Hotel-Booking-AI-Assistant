import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import create_engine
from app.database.models import Base
from app import config

def create_tables():
    engine = create_engine(config.DATABASE_URL)
    Base.metadata.create_all(engine)
    print("Tables successfully created!")

if __name__ == "__main__":
    create_tables()