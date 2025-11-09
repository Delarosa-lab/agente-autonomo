from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

# Canal do YouTube
class Channel(Base):
    __tablename__ = "channels"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    niche = Column(String, nullable=False)
    youtube_url = Column(String, nullable=True)
    monetization = Column(Float, default=0.0)

    contents = relationship("Content", back_populates="channel")

# Conteúdo (vídeos, shorts, etc.)
class Content(Base):
    __tablename__ = "contents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    type = Column(String, nullable=False)  # video_longo, short, ebook
    script = Column(Text)
    upload_date = Column(DateTime, default=datetime.utcnow)
    channel_id = Column(Integer, ForeignKey("channels.id"))

    channel = relationship("Channel", back_populates="contents")

# Tarefas (para agendamento de postagens)
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    task_type = Column(String)
    status = Column(String, default="pendente")
    created_at = Column(DateTime, default=datetime.utcnow)

# Finanças (controle de vendas e reinvestimento)
class Finance(Base):
    __tablename__ = "finances"
    id = Column(Integer, primary_key=True)
    total_earned = Column(Float, default=0.0)
    reinvestment = Column(Float, default=0.0)
    last_update = Column(DateTime, default=datetime.utcnow)
