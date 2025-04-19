from flask import Flask, request
import os
import requests
import asyncio
from dotenv import load_dotenv
from agents.recipe_agent import RecipeAgent

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)
recipe_agent = RecipeAgent()

WHATSAPP_URL = f"https://graph.facebook.com/v17.0/{os.getenv('ID_NUMBER')}/messages"
HEADERS = {
    "Authorization": f"Bearer {os.getenv('API_FACEBOOK')}",
    "Content-Type": "application/json",
}

AUTHORIZED_NUMBER = os.getenv("AUTHORIZED_NUMBER")
processed_messages = set()


def extract_message_data(payload):
    try:
        change = payload.get("entry", [{}])[0].get("changes", [{}])[0]
        value = change.get("value", {})

        message = value.get("messages", [{}])[0]
        contact = value.get("contacts", [{}])[0]
        name = contact.get("profile", {}).get("name", "")

        return {
            "text": message["text"]["body"],
            "from": message["from"],
            "id": message["id"],
            "name": name,
        }
    except Exception as e:
        print("Erro ao extrair mensagem:", e)
        return None


def send_whatsapp_message(to, text):
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"preview_url": False, "body": text},
    }
    response = requests.post(WHATSAPP_URL, headers=HEADERS, json=data)
    print("Mensagem enviada:", response.status_code, response.text)


@app.route("/webhook", methods=["POST"])
def whatsapp_bot():
    incoming = request.get_json()
    print("Recebido:", incoming)

    message_data = extract_message_data(incoming)
    if not message_data:
        return "OK", 200

    msg_text = message_data["text"]
    from_number = message_data["from"]
    message_id = message_data["id"]
    name = message_data["name"]

    if from_number != AUTHORIZED_NUMBER:
        print("Número não autorizado:", from_number)
        return "OK", 200

    if message_id in processed_messages:
        print("Mensagem já processada:", message_id)
        return "OK", 200

    processed_messages.add(message_id)

    # Envia resposta imediata de espera
    send_whatsapp_message(
        from_number,
        f"🧑🏿‍🍳 Aguarde só um instante, *{name}*! Estou preparando sua receita deliciosa... 🍽️✨",
    )

    try:
        resposta = asyncio.run(recipe_agent.process_message(msg_text))
        print("Resposta do agente:", resposta)
        send_whatsapp_message(from_number, resposta)
    except Exception as e:
        print("Erro ao processar mensagem:", e)

    return "OK", 200


@app.route("/webhook", methods=["GET"])
def verify():
    verify_token = os.getenv("VERIFY_TOKEN")
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == verify_token:
        print("Webhook verificado!")
        return challenge, 200

    return "Erro de verificação", 403


if __name__ == "__main__":
    app.run(port=os.getenv("PORT"))
