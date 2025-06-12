# 🤖 AI Call Center (Python-Based)

Welcome to the **AI Call Center**, an intelligent voice and chat assistant built with Python and FastAPI. This project is designed to handle customer service inquiries, order processing, and technical support via **voice calls (VoIP)** and **text chat interfaces**, with integration options for WordPress and other CMS platforms via REST API.

---

## 🎯 Features

- 🔊 **Voice Call Handling** via Twilio or Asterisk
- 💬 **Chat Interface** for web and messaging apps (e.g. WhatsApp)
- 🧠 **Hybrid Response Engine**:
  - Rule-based answers for FAQs
  - LLM-powered responses (via Hugging Face models)
- 🗣️ **Speech-to-Text (STT)** with Whisper or Vosk
- 🔊 **Text-to-Speech (TTS)** with Kokoro-82M or gTTS
- 💾 **Conversation Logging** (text/audio)
- 🌐 **WordPress Integration** via REST API

---

## 🏗️ Project Structure

```
ai_call_center/
├── main.py
├── config.py
├── requirements.txt
├── voice_interface/
├── chat_interface/
├── speech_to_text/
├── text_to_speech/
├── nlp_engine/
├── api_interface/
├── logs/
└── utils/
```

---

## 🚀 Getting Started

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/ai_call_center.git
   cd ai_call_center
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Run the FastAPI app:
   ```
   uvicorn main:app --reload
   ```

---

## 🔌 WordPress Integration

You can build a lightweight WordPress plugin to send user input via REST API to the `/chat` endpoint and display the response on your site.

---

## 📁 Logs

All conversations are logged in JSON format and saved under the `logs/` directory for analytics and review.

---

## 👨‍💻 Author

Developed by [Mehdi Jahani]