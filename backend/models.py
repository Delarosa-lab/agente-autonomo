# backend/models.py

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class VideoTask(Base):
    __tablename__ = "video_tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    niche = Column(String)
    status = Column(String, default="pending")
    video_type = Column(String, default="short")  # short or long
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class SaleRecord(Base):
    __tablename__ = "sale_records"
    id = Column(Integer, primary_key=True)
    product_name = Column(String)
    amount = Column(Float)
    reinvested = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

def get_engine():
    db_url = os.getenv("DATABASE_URL", "sqlite:///data.db")
    return create_engine(db_url)

def create_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    create_tables()
    print("✅ Tabelas criadas com sucesso!")
