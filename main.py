import json
from app.agents.conversation_agent import ConversationAgent
from app.agents.structuring_agent import StructuringAgent
from app.services.email_service import EmailService
from app.database.repository import Repository
import uuid

agent = ConversationAgent()
structuring_agent = StructuringAgent()
email_service = EmailService()
repo = Repository()

session_id = str(uuid.uuid4())
history = []

print("Hotel Bot Test - type 'quit' to stop\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        break

    result = agent.get_response(history, user_input)
    print(f"Bot: {result['reply']}\n")

    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": result['reply']})

    repo.save_messages(session_id, history)

    if result['is_complete']:
        print("✅ Booking info complete!\n")
        print("--- Extracting structured data ---")

        booking_data = structuring_agent.extract_booking_data(history)
        print(json.dumps(booking_data, indent=2))

        if booking_data:
            booking_data["session_id"] = session_id
            inquiry = repo.save_booking_inquiry(booking_data)
            print(f"\n✅ Saved to database (ID: {inquiry.id})")

            sent = email_service.send_booking_email(booking_data)
            if sent:
                repo.mark_email_sent(inquiry.id)
                print("✅ Email sent to owner!")

        repo.mark_conversation_complete(session_id)
        break

repo.close()