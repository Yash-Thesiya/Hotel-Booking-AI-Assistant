import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.database.models import Conversation, BookingInquiry
from app import config

engine = create_engine(config.DATABASE_URL)
Session = sessionmaker(bind=engine)

class Repository:

    def __init__(self):
        self.session = Session()

    def get_or_create_conversation(self, session_id: str):
        conv = self.session.query(Conversation).filter_by(
            session_id=session_id
        ).first()

        if not conv:
            conv = Conversation(
                session_id=session_id,
                messages=json.dumps([]),
                is_complete=False
            )
            self.session.add(conv)
            self.session.commit()

        return conv

    def save_messages(self, session_id: str, messages: list):
        conv = self.session.query(Conversation).filter_by(
            session_id=session_id
        ).first()

        if conv:
            conv.messages = json.dumps(messages)
            conv.updated_at = datetime.utcnow()
            self.session.commit()

    def mark_conversation_complete(self, session_id: str):
        conv = self.session.query(Conversation).filter_by(
            session_id=session_id
        ).first()

        if conv:
            conv.is_complete = True
            self.session.commit()

    def save_booking_inquiry(self, data: dict):
        inquiry = BookingInquiry(**data)
        self.session.add(inquiry)
        self.session.commit()
        return inquiry

    def mark_email_sent(self, inquiry_id: int):
        inquiry = self.session.query(BookingInquiry).filter_by(
            id=inquiry_id
        ).first()
        if inquiry:
            inquiry.email_sent = True
            self.session.commit()

    def close(self):
        self.session.close()