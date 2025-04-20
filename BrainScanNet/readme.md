# BrainScanNet

**BrainScanNet** is a cutting-edge AI project developed to assist in the analysis and interpretation of brain scans. Leveraging advanced deep learning models, BrainScanNet aims to provide accurate and efficient diagnostic support for medical professionals.

Originally developed by me and my friends. You can view the original repository [here](https://github.com/gabrieldadcarvalho/BrainScanNet).

![Model Architecture](https://raw.githubusercontent.com/gabrieldadcarvalho/BrainScanNet/refs/heads/main/plots/brainscannet_structure.jpg)

---

## 🚀 Features

- **Automated Analysis**: Utilizes state-of-the-art neural networks to analyze brain scans.
- **Diagnostic Support**: Offers insights and potential diagnoses based on image data.
- **User-Friendly Interface**: Designed with an intuitive interface for medical professionals.
- **System Integration**: Easily integrates with existing hospital systems.

---

## 🛠 Prerequisites

1. A Meta developer account — [Create one here](https://developers.facebook.com/).
2. A Meta Business App — [Learn how to create one](https://developers.facebook.com/docs/development/create-an-app/).

---

## 📦 Getting Started

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/BrainScanNet.git
   cd BrainScanNet
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**:
   Create a `.env` file based on `.env.example` and update your variables accordingly.

4. **Run the Application**:
   ```bash
   python main.py
   ```

---

## 📡 WhatsApp Cloud API Integration

The project uses the WhatsApp Cloud API to send and receive messages.

### Step 1: Select Phone Numbers

- Add WhatsApp to your app.
- Use your test number (limited to 5 test numbers).
- Add your number to receive a verification code via WhatsApp.

### Step 2: Send Messages via API

1. Get a 24-hour access token.
2. Use the `curl` example provided or convert it to [Python with requests](https://github.com/daveebbelaar/python-whatsapp-bot/blob/main/start/whatsapp_quickstart.py).
3. Create your `.env` file using `.env.example`.
4. Expect the "Hello World" message within ~60–120 seconds.

### Extend Token Duration

- Create a [System User](https://business.facebook.com/settings/system-users).
- Assign the WhatsApp app and generate a token.
- Select full permissions.

Add to `.env`:
- `APP_ID`, `APP_SECRET`, `RECIPIENT_WAID`, `VERSION`, `ACCESS_TOKEN`

---

## 🌐 Configure Webhooks

### Step 1: Expose Your Localhost via ngrok

1. [Sign up for ngrok](https://ngrok.com).
2. Install and authenticate the ngrok agent.
3. Create a free domain:
   ```bash
   ngrok http 8000 --domain your-domain.ngrok-free.app
   ```

### Step 2: Configure Webhook in Meta Dashboard

- Use your ngrok URL + `/webhook`.
- Add your custom `VERIFY_TOKEN`.
- Subscribe to **messages** in webhook fields.
- Run your Flask app and test the webhook.

---

## 🧪 Test the Integration

1. Send a brain scan image via WhatsApp.
2. The app receives the image and logs request data.
3. The bot replies with a classification.

---

## 💡 Usage

Upload brain scan images through WhatsApp. The system processes the image and returns diagnostic suggestions automatically.

---

## 🤝 Contributing

We welcome contributions! Please fork the repository and submit a pull request. Ensure your code meets project standards.

---

## 📄 License

Licensed under the Attribution-ShareAlike 4.0 International License. See the [LICENSE](LICENSE) file for more info.

---

## 📬 Contact

For questions or support: [gabriedadcarvalho@gmail.com](mailto:gabriedadcarvalho@gmail.com)
