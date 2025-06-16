from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from nlp_engine.response_generator import generate_response
from text_to_speech.kokoro_handler import synthesize_speech
from pathlib import Path
import uuid
import os

# برای مسیر مطلق:
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # فرض بر اینکه chat_interface زیر پروژه است
AUDIO_DIR = os.path.join(PROJECT_ROOT, "outputs", "audio")

# تنظیم مسیر پوشه قالب‌ها
templates = Jinja2Templates(directory="chat_interface/templates")
router = APIRouter()

@router.get("/ui", response_class=HTMLResponse)
async def chat_ui(request: Request):
    """
    مسیر GET برای نمایش رابط کاربری چت.
    این تابع فایل 'chat.html' را رندر کرده و به مرورگر ارسال می‌کند.
    """
    return templates.TemplateResponse("chat.html", {"request": request})

@router.post("/")
async def chat_endpoint(request: Request):
    """
    مسیر POST برای دریافت پیام‌های چت از رابط کاربری و تولید پاسخ متنی و صوتی.
    """
    try:
        data = await request.json()
        user_message = data.get("text")

        if not user_message:
            return {"reply": "Please enter a message."}

        # تولید پاسخ متنی
        bot_response_text = generate_response(user_message)

        # تولید پاسخ صوتی با استفاده از kokoro TTS
        os.makedirs(AUDIO_DIR, exist_ok=True)
        audio_filename = f"{uuid.uuid4().hex}.wav"
        audio_output_dir = Path(AUDIO_DIR)
        audio_path = synthesize_speech(bot_response_text, audio_output_dir, file_name=audio_filename)
        audio_url = f"/static/audio/{audio_filename}"

        return {
            "reply": bot_response_text,
            "reply_audio_url": audio_url
        }
    except Exception as e:
        print(f"Error in chat_endpoint: {e}")
        return {"reply": "An error occurred while processing your message."}