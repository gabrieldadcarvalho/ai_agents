from flask import Flask, request, jsonify
import os
import requests
import asyncio
from dotenv import load_dotenv
from model.data_preprocessing import transform_input_data
from model.brainscannet import load_model
from PIL import Image
import tempfile
import torch

app = Flask(__name__)
load_dotenv()

WHATSAPP_URL = f"https://graph.facebook.com/v17.0/{os.getenv('ID_NUMBER')}/messages"
HEADERS = {
    "Authorization": f"Bearer {os.getenv('API_FACEBOOK')}",
    "Content-Type": "application/json",
}

AUTHORIZED_NUMBER = os.getenv("AUTHORIZED_NUMBER")
processed_messages = set()
classes = ["Tumor Glioma", "Tumor Meningioma", "Sem tumor", "Tumor Pituitária"]


def extract_image_id(payload):
    try:
        message = (
            payload.get("entry", [{}])[0]
            .get("changes", [{}])[0]
            .get("value", {})
            .get("messages", [{}])[0]
        )
        if message.get("type") == "image":
            return message["image"]["id"]
        return None
    except Exception as e:
        print("Erro ao extrair imagem:", e)
        return None


def download_whatsapp_image(media_id):
    # Passo 1: Obter o URL da mídia
    media_url = f"https://graph.facebook.com/v17.0/{media_id}"
    params = {"access_token": os.getenv("API_FACEBOOK")}
    response = requests.get(media_url, params=params)
    if response.status_code != 200:
        print("Erro ao obter metadata da imagem:", response.text)
        return None

    image_url = response.json().get("url")
    if not image_url:
        print("URL da imagem não encontrada.")
        return None

    # Passo 2: Fazer o download da imagem
    headers = {"Authorization": f"Bearer {os.getenv('API_FACEBOOK')}"}
    image_response = requests.get(image_url, headers=headers)
    if image_response.status_code == 200:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
            f.write(image_response.content)
            print("Imagem salva em:", f.name)
            return f.name
    else:
        print("Erro ao baixar imagem:", image_response.text)
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

    from_number = None 
    name = "usuário"

    try:
        value = incoming["entry"][0]["changes"][0]["value"]
        message = value["messages"][0]
        from_number = message["from"]
        message_id = message["id"]
        name = value["contacts"][0]["profile"]["name"]

        if from_number != AUTHORIZED_NUMBER or message_id in processed_messages:
            return "OK", 200

        processed_messages.add(message_id)

        send_whatsapp_message(
            from_number,
            f"🧠 Aguarde só um instante, *{name}*! Estou analisando sua tomografia... 🧬📊",
        )

        image_id = extract_image_id(incoming)
        if image_id:
            local_image_path = download_whatsapp_image(image_id)
            if local_image_path:
                image_tensor = transform_input_data(local_image_path).unsqueeze(0)
                print(image_tensor)
                model = load_model()
                model.eval()
                output = model(image_tensor)
                prediction = torch.argmax(output, dim=1).item()
                send_whatsapp_message(
                    from_number,
                    f"📊 Resultado da análise: *{classes[prediction]}*",
                )
            else:
                send_whatsapp_message(
                    from_number, "❌ Erro ao baixar a imagem da tomografia."
                )
        else:
            send_whatsapp_message(
                from_number,
                "❗ Por favor, envie uma imagem da tomografia para análise.",
            )

    except Exception as e:
        print("Erro ao processar webhook:", e)
        if from_number:
            send_whatsapp_message(
                from_number,
                "⚠️ Ocorreu um erro ao processar sua imagem. Tente novamente.",
            )

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
    app.run(port=int(os.getenv("PORT", 5000)))
