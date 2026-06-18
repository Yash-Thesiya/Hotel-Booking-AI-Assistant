from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, unique=True)
    messages = Column(Text)  # JSON string of full chat history
    is_complete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class BookingInquiry(Base):
    __tablename__ = "booking_inquiries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String)
    guest_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    check_in = Column(String, nullable=True)
    check_out = Column(String, nullable=True)
    guests_count = Column(Integer, nullable=True)
    rooms_needed = Column(Integer, nullable=True)
    room_type = Column(String, nullable=True)
    budget = Column(String, nullable=True)
    special_requests = Column(Text, nullable=True)
    email_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)