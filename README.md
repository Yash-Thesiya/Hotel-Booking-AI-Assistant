# Hotel Booking AI Assistant

An AI-powered chat assistant that handles hotel booking inquiries through natural conversation. Customers chat with the bot like they would with a hotel receptionist, and the assistant automatically extracts structured booking details and emails them to the hotel owner.

## What It Does

A customer opens the chat widget and talks to the assistant in plain language — no forms, no dropdowns. The assistant asks for the information it needs one or two questions at a time (name, phone number, check-in/check-out dates, number of guests, rooms needed, room type preference, budget, and any special requests). Once everything is collected, it summarizes the booking back to the customer for confirmation. After confirmation, the conversation is converted into structured data, saved to the database, and a clean formatted email is sent straight to the hotel owner's inbox.

## Architecture

```
Customer (Streamlit Chat)
        |
        v
Conversation Agent  (collects booking details through natural dialogue)
        |
        v
PostgreSQL Database  (every message saved as it happens)
        |
        v
Structuring Agent  (converts finished conversation into structured JSON)
        |
        v
PostgreSQL Database  (booking_inquiries table)
        |
        v
Email Service  (formats HTML email)
        |
        v
Hotel Owner's Inbox
```

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python |
| Package Manager | UV |
| Database | PostgreSQL (via Docker) |
| ORM | SQLAlchemy |
| AI Provider | OpenRouter (Claude models) |
| Data Validation | Pydantic |
| Frontend | Streamlit |
| Email | Gmail SMTP |

## Project Structure

```
hotel-booking-bot/
├── app/
│   ├── config.py                  # Environment variables, OpenRouter client setup
│   ├── agents/
│   │   ├── conversation_agent.py  # Handles the live chat with the customer
│   │   └── structuring_agent.py   # Extracts structured data from finished chats
│   ├── database/
│   │   ├── models.py              # Conversation and BookingInquiry tables
│   │   ├── create_tables.py       # One-time table setup script
│   │   └── repository.py         # All database read/write operations
│   └── services/
│       └── email_service.py       # Formats and sends booking emails
├── frontend/
│   └── chat_app.py                 # Streamlit chat interface
├── docker-compose.yml              # Local PostgreSQL container
├── .env                            # Configuration (not committed to version control)
├── main.py                         # CLI test entry point
└── pyproject.toml                  # Dependencies
```

## How The Two Agents Work Together

**Conversation Agent** is the one the customer actually talks to. It runs on every message, gets the full chat history as context, and decides what to ask next. It never asks for information it already has, and it keeps responses short and natural. When it has collected all eight required fields and the customer has confirmed the summary, it appends a hidden signal (`BOOKING_COMPLETE`) to its reply, which the application code detects to trigger the next stage.

**Structuring Agent** never talks to the customer. It only runs once, after the conversation is marked complete. It reads the entire conversation transcript and returns a single JSON object with the data converted into clean fields and proper date formats — this is what actually gets saved to the database and used to build the email.

Separating these two agents keeps each one focused: the conversation agent optimizes for a good chat experience, and the structuring agent optimizes for accurate, consistent data extraction.

## Database Schema

**conversations**
| Column | Type | Description |
|---|---|---|
| id | Integer | Primary key |
| session_id | String | Unique per chat session |
| messages | Text | Full chat history, stored as JSON |
| is_complete | Boolean | Whether booking info has been fully collected |
| created_at | DateTime | When the session started |
| updated_at | DateTime | Last message timestamp |

**booking_inquiries**
| Column | Type | Description |
|---|---|---|
| id | Integer | Primary key |
| session_id | String | Links back to the conversation |
| guest_name | String | Customer name |
| phone | String | Customer phone number |
| check_in | String | Check-in date (YYYY-MM-DD) |
| check_out | String | Check-out date (YYYY-MM-DD) |
| guests_count | Integer | Number of guests |
| rooms_needed | Integer | Number of rooms requested |
| room_type | String | AC, Non-AC, or both |
| budget | String | Budget range per night |
| special_requests | Text | Any extra requests |
| email_sent | Boolean | Whether the owner has been notified |
| created_at | DateTime | When the inquiry was finalized |

## Setup

### 1. Install dependencies

```bash
uv venv
.venv\Scripts\activate
uv add sqlalchemy psycopg2-binary openai pydantic python-dotenv streamlit
```

### 2. Start the database

```bash
docker compose up -d
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=5433
DB_NAME=hotel_bot
DB_USER=postgres
DB_PASSWORD=postgres

OPENROUTER_API_KEY=your_openrouter_key

HOTEL_NAME=Your Hotel Name
OWNER_EMAIL=owner@example.com
MY_EMAIL=sending_email@gmail.com
EMAIL_APP_PASSWORD=your_gmail_app_password
```

### 4. Create database tables

```bash
python -m app.database.create_tables
```

### 5. Run the app

```bash
streamlit run frontend/chat_app.py
```

## Future Improvements

- Room availability checks against a live inventory table before confirming a booking
- Support for multiple hotel properties from a single deployment
- Input validation for phone numbers and dates before they reach the structuring agent
- WhatsApp Business API integration as an alternative front end
- Deployment to a hosting platform for a permanent public link