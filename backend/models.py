from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

# YouTube Channel
class Channel(Base):
    __tablename__ = 'channels'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    niche = Column(String(255))
    subscribers = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

# Task (shorts, long videos, ebooks, etc.)
class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer)
    type = Column(String(50))
    status = Column(String(50), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)

# Content (scripts, descriptions, titles)
class Content(Base):
    __tablename__ = 'contents'
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer)
    title = Column(String(255))
    script = Column(Text)
    type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

# Finance (affiliate, ebooks, reinvestments)
class Finance(Base):
    __tablename__ = 'finances'
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer)
    revenue = Column(Float, default=0.0)
    reinvestment = Column(Float, default=0.2)
    updated_at = Column(DateTime, default=datetime.utcnow)
