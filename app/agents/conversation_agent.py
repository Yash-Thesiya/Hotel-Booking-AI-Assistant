import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import json
from app import config

SYSTEM_PROMPT = """You are a friendly hotel booking assistant for {hotel_name}.
Your job is to chat naturally with customers and collect this booking information:

1. Guest name
2. Phone number
3. Check-in date (dd/mm/yy)
4. Check-out date (dd/mm/yy)
5. Number of guests
6. Number of rooms needed
7. Room type preference (AC or Non-AC)
8. Budget range (per night)
9. Any special requests (optional)

RULES:
- Be warm, friendly, and conversational - like a helpful hotel receptionist
- Ask ONE or TWO questions at a time, not all at once
- If the customer gives multiple details in one message, acknowledge all of them
- Don't ask for information already provided
- Keep responses short and natural (2-3 sentences max)
- Once you have ALL required information (1-8), summarize it back to confirm
- After customer confirms, say exactly: "BOOKING_COMPLETE" at the end of your message
- Be patient if customer asks questions about the hotel - answer generally and continue collecting info

Current hotel: {hotel_name}
"""

class ConversationAgent:

    def __init__(self):
        self.client = config.get_openrouter_client()
        self.model = "anthropic/claude-3-haiku"

    def get_response(self, conversation_history: list, user_message: str):
        messages = [
            {
                "role": "system", 
                "content": SYSTEM_PROMPT.format(hotel_name=config.HOTEL_NAME)
            }
        ]

        for msg in conversation_history:
            messages.append(msg)

        messages.append({"role": "user", "content": user_message})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )

            ai_reply = response.choices[0].message.content

            is_complete = "BOOKING_COMPLETE" in ai_reply
            clean_reply = ai_reply.replace("BOOKING_COMPLETE", "").strip()

            return {
                "reply": clean_reply,
                "is_complete": is_complete
            }

        except Exception as e:
            print(f"Conversation agent error: {e}")
            return {
                "reply": "Sorry, I'm having trouble right now. Could you please try again?",
                "is_complete": False
            }