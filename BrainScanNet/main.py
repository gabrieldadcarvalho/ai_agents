from flask import Flask, request, jsonify
import os
import requests
import asyncio
import logging
from functools import lru_cache
from dotenv import load_dotenv
from model.data_preprocessing import transform_input_data
from model.brainscannet import load_model
from PIL import Image
import tempfile
import torch

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
load_dotenv()

WHATSAPP_URL = f"https://graph.facebook.com/v22.0/{os.getenv('ID_NUMBER')}/messages"
HEADERS = {
    "Authorization": f"Bearer {os.getenv('API_FACEBOOK')}",
    "Content-Type": "application/json",
}

AUTHORIZED_NUMBER = os.getenv("AUTHORIZED_NUMBER")
processed_messages = set()


# Class definitions
class BrainClasses:
    GLIOMA = "Tumor Glioma"
    MENINGIOMA = "Tumor Meningioma"
    NO_TUMOR = "Sem tumor"
    PITUITARY = "Tumor Pituitária"

    @classmethod
    def get_class_list(cls):
        return [cls.GLIOMA, cls.MENINGIOMA, cls.NO_TUMOR, cls.PITUITARY]


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
        logger.error(f"Error extracting image ID: {e}")
        return None


def download_whatsapp_image(media_id):
    # Step 1: Get the media URL
    media_url = f"https://graph.facebook.com/v22.0/{media_id}"
    params = {"access_token": os.getenv("API_FACEBOOK")}

    try:
        response = requests.get(media_url, params=params)
        response.raise_for_status()

        image_url = response.json().get("url")
        if not image_url:
            logger.error("Image URL not found")
            return None

        # Step 2: Download the image
        headers = {"Authorization": f"Bearer {os.getenv('API_FACEBOOK')}"}
        image_response = requests.get(image_url, headers=headers)
        image_response.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
            f.write(image_response.content)
            logger.info(f"Image saved to: {f.name}")
            return f.name

    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading image: {e}")
        return None


def send_whatsapp_message(to, text):
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"preview_url": False, "body": text},
    }
    try:
        response = requests.post(WHATSAPP_URL, headers=HEADERS, json=data)
        response.raise_for_status()
        logger.info(f"Message sent: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending WhatsApp message: {e}")


@lru_cache(maxsize=1)
def get_model():
    """Load model with caching to avoid reloading for each request"""
    return load_model()


def analyze_brain_scan(image_path):
    """Analyze brain scan and return prediction class"""
    try:
        image_tensor = transform_input_data(image_path).unsqueeze(0)
        model = get_model()

        with torch.no_grad():  # Disable gradient calculation for inference
            output = model(image_tensor)
            prediction = torch.argmax(output, dim=1).item()

        return BrainClasses.get_class_list()[prediction]
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return None


@app.route("/webhook", methods=["POST"])
def whatsapp_bot():
    incoming = request.get_json()
    logger.info(f"Received: {incoming}")

    from_number = None
    name = "usuário"

    try:
        value = incoming["entry"][0]["changes"][0]["value"]
        message = value["messages"][0]
        from_number = message["from"]
        message_id = message["id"]
        name = value["contacts"][0]["profile"]["name"]

        # Skip if not from authorized number or already processed
        if from_number != AUTHORIZED_NUMBER or message_id in processed_messages:
            return "OK", 200

        processed_messages.add(message_id)

        # Process only the latest 100 messages to avoid memory growth
        if len(processed_messages) > 100:
            processed_messages.clear()
            processed_messages.add(message_id)

        send_whatsapp_message(
            from_number,
            f"🧠 Aguarde só um instante, *{name}*! Estou analisando sua tomografia... 🧬📊",
        )

        image_id = extract_image_id(incoming)
        if not image_id:
            send_whatsapp_message(
                from_number,
                "❗ Por favor, envie uma imagem da tomografia para análise.",
            )
            return "OK", 200

        local_image_path = download_whatsapp_image(image_id)
        if not local_image_path:
            send_whatsapp_message(
                from_number, "❌ Erro ao baixar a imagem da tomografia."
            )
            return "OK", 200

        # Analyze the image and send result
        result = analyze_brain_scan(local_image_path)
        if result:
            send_whatsapp_message(
                from_number,
                f"📊 Resultado da análise: *{result}*",
            )
        else:
            send_whatsapp_message(
                from_number,
                "⚠️ Ocorreu um erro ao processar sua imagem. Tente novamente.",
            )

        # Clean up the temporary file
        try:
            os.unlink(local_image_path)
        except Exception as e:
            logger.warning(f"Error deleting temporary file: {e}")

    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
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
        logger.info("Webhook verified!")
        return challenge, 200

    return "Verification error", 403


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logger.info(f"Starting BrainScanNet on port {port}")
    app.run(port=port)