# CookAi

## Objective

The user send a message on whatsapp with a list of ingredients and the AI agent interprets the message and returns a list of recipes.

## Project Structure

Whatsapp User -> Twilio Whatsapp API (Webhook) -> Backend Server (Flask / FastAPI) -> AI Agent (CrewAI with Ollama) -> Response -> Twilio Whatsapp API -> Whatsapp User

## Directory Structure

```
cook/
├── README.md
├── requirements.txt
├── .env.example
└── app/
    ├── __init__.py
    ├── main.py
    └── agents/
        ├── __init__.py
        └── recipe_agent.py
```
# Key Components:
* requirements.txt: Contains all necessary Python dependencies
* .env.example: Template for environment variables
* main.py: FastAPI application with webhook endpoint
* recipe_agent.py: AI agent implementation using CrewAI and Ollama

# Features:
* WhatsApp integration via Twilio webhook
* FastAPI backend server
* AI-powered recipe generation using CrewAI and Ollama
* Environment variable configuration
* Async processing of messages

# To get started:
* Copy .env.example to .env and fill in your Twilio credentials
* Install dependencies:

```bash
pip install -r requirements.txt
```

* Make sure Ollama is running locally with the specified model
* Start the server:

```bash
python -m app.main
```

The system will:
* Receive WhatsApp messages via Twilio webhook
* Process the ingredients using the AI agent
* Generate recipe suggestions
* Send the response back via WhatsApp