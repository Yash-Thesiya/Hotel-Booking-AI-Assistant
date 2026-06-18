import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import uuid
import json

from app.agents.conversation_agent import ConversationAgent
from app.agents.structuring_agent import StructuringAgent
from app.services.email_service import EmailService
from app.database.repository import Repository
from app import config

st.set_page_config(
    page_title=f"{config.HOTEL_NAME} - Booking Assistant",
    page_icon="🏨",
    layout="centered"
)

# --- Dark Theme Custom CSS ---
st.markdown("""
<style>
    .stApp {
        background-color: #0d0d0f;
    }

    .stChatMessage {
        background-color: transparent !important;
    }

    [data-testid="stChatMessageContent"] {
        background-color: #1c1c20 !important;
        color: #e8e8e8 !important;
        border-radius: 14px 14px 14px 4px !important;
        padding: 12px 16px !important;
    }

    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
        background-color: #534AB7 !important;
        color: #f5f4ff !important;
        border-radius: 14px 14px 4px 14px !important;
    }

    .stChatInput textarea {
        background-color: #1c1c20 !important;
        color: #e8e8e8 !important;
        border: 0.5px solid #2a2a2e !important;
        border-radius: 20px !important;
    }

    .stChatInput button {
        background-color: #534AB7 !important;
        border-radius: 50% !important;
    }

    h1, h2, h3, p, span, div {
        color: #f0f0f0;
    }

    [data-testid="stCaptionContainer"] {
        color: #7F77DD !important;
    }

    .stAlert {
        background-color: #1c1c20 !important;
        color: #e8e8e8 !important;
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize session state ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "booking_complete" not in st.session_state:
    st.session_state.booking_complete = False

if "agent" not in st.session_state:
    st.session_state.agent = ConversationAgent()

if "structuring_agent" not in st.session_state:
    st.session_state.structuring_agent = StructuringAgent()

# --- Header ---
st.markdown(f"""
<div style="display: flex; align-items: center; gap: 12px; padding: 0.5rem 0 1.5rem 0; border-bottom: 0.5px solid #2a2a2e; margin-bottom: 1rem;">
    <div style="width: 40px; height: 40px; border-radius: 50%; background: #7F77DD; display: flex; align-items: center; justify-content: center; font-size: 20px;">
        🏨
    </div>
    <div>
        <p style="font-size: 16px; font-weight: 600; margin: 0; color: #f0f0f0;">{config.HOTEL_NAME}</p>
        <p style="font-size: 13px; color: #7F77DD; margin: 0;">Online</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Show welcome message if no messages yet ---
if not st.session_state.messages:
    welcome_msg = f"Welcome to {config.HOTEL_NAME}! 👋 I'm here to help you book a room. May I start with your name?"
    st.session_state.messages.append({
        "role": "assistant", 
        "content": welcome_msg
    })

# --- Display chat history ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- Booking complete banner ---
if st.session_state.booking_complete:
    st.success("✅ Your booking inquiry has been submitted! Our team will contact you shortly.")
    if st.button("Start New Booking"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.booking_complete = False
        st.rerun()

# --- Chat input ---
else:
    user_input = st.chat_input("Type your message...")

    if user_input:
        # Show user message
        st.session_state.messages.append({
            "role": "user", 
            "content": user_input
        })
        with st.chat_message("user"):
            st.write(user_input)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Typing..."):
                history_for_agent = st.session_state.messages[:-1]
                result = st.session_state.agent.get_response(
                    history_for_agent, user_input
                )

            st.write(result["reply"])

        st.session_state.messages.append({
            "role": "assistant", 
            "content": result["reply"]
        })

        # Save to database
        repo = Repository()
        repo.save_messages(st.session_state.session_id, st.session_state.messages)

        # Check if booking is complete
        if result["is_complete"]:
            with st.spinner("Finalizing your booking..."):
                booking_data = st.session_state.structuring_agent.extract_booking_data(
                    st.session_state.messages
                )

                if booking_data:
                    booking_data["session_id"] = st.session_state.session_id
                    inquiry = repo.save_booking_inquiry(booking_data)

                    email_service = EmailService()
                    sent = email_service.send_booking_email(booking_data)

                    if sent:
                        repo.mark_email_sent(inquiry.id)

                    repo.mark_conversation_complete(st.session_state.session_id)
                    st.session_state.booking_complete = True

        repo.close()
        st.rerun()