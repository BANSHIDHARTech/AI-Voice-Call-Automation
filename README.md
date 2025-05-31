# AI Voice Agent System (PoC-1)

A Python-based AI voice assistant that handles inbound and outbound calls to automate customer support tasks.

## 🎯 Features

- **Outbound Calls**: Initiate voice calls using TTS, capture responses with STT, and extract intents
- **Inbound Calls**: Receive calls via Twilio/Vapi, transcribe voice, and route appropriately
- **Multi-Language Support**: English and Hindi language support with auto-detection
- **Intent Recognition**: Extract customer intent using OpenAI or rule-based logic
- **Call Logging**: Store detailed call records with transcripts and intents

## 🛠️ Architecture

```
├── app/
│   ├── database/       # Database connection and initialization
│   ├── models/         # SQLAlchemy database models
│   ├── routes/         # API route handlers
│   ├── schemas/        # Pydantic schemas for API
│   ├── services/       # Business logic services
│   └── utils/          # Utility functions and configs
├── main.py             # FastAPI application entry point
├── requirements.txt    # Project dependencies
└── .env                # Environment variables (create from .env.example)
```

## 📋 Prerequisites

- Python 3.8 or higher
- SQLite (development) or PostgreSQL (production)
- API keys for:
  - ElevenLabs (TTS)
  - OpenAI (STT and intent recognition)
  - Twilio or Vapi (optional, for real call handling)

## 🚀 Setup and Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create `.env` file from example:
   ```
   cp .env.example .env
   ```
5. Update the `.env` file with your API keys
6. Run the application:
   ```
   python main.py
   ```
7. Visit http://localhost:8000/docs for the Swagger UI

## 📞 Testing the Voice Agent

### Simulating an Outbound Call

Make a POST request to `/calls/outbound` with the following payload:

```json
{
  "phone_number": "+1234567890",
  "message": "Hello, this is an automated call from our customer service. How can we help you today?",
  "language": "en"
}
```

### Simulating an Inbound Call

Make a POST request to `/admin/simulate-call` with the following parameters:

- `phone_number`: The caller's phone number
- `message`: The message from the caller
- `language`: The language of the message (en/hi)

## 🌐 API Endpoints

- **GET /**: Health check endpoint
- **POST /calls/outbound**: Initiate an outbound call
- **GET /calls/{call_id}**: Get details for a specific call
- **GET /calls**: List all calls with optional filtering
- **POST /webhooks/twilio**: Webhook for Twilio call events
- **POST /webhooks/vapi**: Webhook for Vapi call events
- **GET /admin/analytics**: Get call analytics
- **GET /admin/intents**: Get summary of detected intents
- **POST /admin/simulate-call**: Simulate an inbound call for testing

## 📊 Database Schema

- **calls**: Call records with metadata, transcripts, and intents
- **recordings**: Audio recordings associated with calls
- **call_actions**: Actions taken based on call intents
- **tickets**: Support tickets created from calls

## 🔄 Call Flow

1. **Outbound Call**:
   - System initiates a call using Twilio/Vapi
   - TTS delivers the message to the recipient
   - STT captures and transcribes the response
   - Intent recognition extracts the customer's intent
   - System performs actions based on the intent

2. **Inbound Call**:
   - Customer calls the system's phone number
   - System answers with a welcome message
   - STT captures and transcribes the customer's speech
   - Intent recognition extracts the customer's intent
   - System performs actions based on the intent
   - Call is routed to a live agent if needed

## 📝 Notes

- This is a proof of concept (PoC) with simulated functionality for some external services
- For production use, enable real API calls by setting `MOCK_EXTERNAL_SERVICES=false`
- Add proper error handling and retry mechanisms for production deployment