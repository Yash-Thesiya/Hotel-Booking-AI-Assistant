import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import json
from app.agents.conversation_agent import config

SYSTEM_PROMPT = """You are a data extraction expert.
Extract booking information from this hotel conversation and 
return ONLY valid JSON in this exact format, nothing else:

{
    "guest_name": "full name or null",
    "phone": "phone number or null",
    "check_in": "YYYY-MM-DD format or null",
    "check_out": "YYYY-MM-DD format or null",
    "guests_count": number or null,
    "rooms_needed": number or null,
    "room_type": "AC or Non-AC or null",
    "budget": "budget description or null",
    "special_requests": "any special requests or null"
}

IMPORTANT:
- Convert dates to YYYY-MM-DD format. Assume current year is 2026 
  if year not mentioned.
- If a date like "20/06" is given, interpret as DD/MM format 
  (Indian format) unless context suggests otherwise.
- Return ONLY the JSON object, no extra text or explanation.
"""

class StructuringAgent:

    def __init__(self):
        self.client = config.get_openrouter_client()
        self.model = "anthropic/claude-3-haiku"

    def extract_booking_data(self, conversation_history: list):
        conversation_text = ""
        for msg in conversation_history:
            role = "Customer" if msg["role"] == "user" else "Bot"
            conversation_text += f"{role}: {msg['content']}\n"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Conversation:\n\n{conversation_text}"}
                ],
                temperature=0.1
            )

            content = response.choices[0].message.content
            content = content.strip()

            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]

            data = json.loads(content)
            return data

        except Exception as e:
            print(f"Structuring agent error: {e}")
            return None