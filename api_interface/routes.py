from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel # اضافه شده: برای تعریف ساختار پیام ورودی
import os
import uuid # برای تولید نام فایل منحصر به فرد

# ایمپورت توابع از ماژول مربوط به Whisper
from speech_to_text.whisper_handler import transcribe_audio_file
# فعال شده: برای اتصال به موتور NLP
from nlp_engine.response_generator import generate_response 

router = APIRouter()

# مدل برای ورودی پیام چت متنی
class MessageInput(BaseModel):
    text: str
    source: str  # chat | voice
    lang: str = "en"

# یک مسیر (endpoint) برای تست اتصال اولیه API
@router.get("/api/health")
async def api_health_check():
    """
    بررسی سلامت API.
    """
    return {"status": "ok", "message": "API is healthy"}

# مسیر برای دریافت پیام متنی (از رابط کاربری چت یا پس از تبدیل صوت)
@router.post("/chat")
def chat_response(data: MessageInput):
    """
    پیام متنی را دریافت کرده و آن را به موتور NLP می فرستد تا پاسخ تولید کند.
    """
    print(f"Received text message from {data.source}: {data.text}")
    reply_text = generate_response(data.text)
    print(f"Generated NLP reply: {reply_text}")
    return {"reply": reply_text}

# مسیر برای دریافت فایل صوتی و تبدیل آن به متن
@router.post("/api/process_audio")
async def process_audio_endpoint(
    audio_file: UploadFile = File(..., description="فایل صوتی برای پردازش (WAV, MP3, FLAC, OGG, WEBM)"),
    language: str = Form("persian", description="زبان فایل صوتی (مثلاً 'persian', 'english')"),
    task: str = Form("transcribe", description="وظیفه Whisper ('transcribe' یا 'translate')")
):
    """
    یک فایل صوتی را دریافت کرده، آن را به متن تبدیل می کند.
    متن تبدیل شده به صورت JSON برگردانده می شود.
    """
    if not audio_file.filename.lower().endswith(('.wav', '.mp3', '.flac', '.ogg', '.webm')):
        raise HTTPException(status_code=400, detail="فرمت فایل صوتی پشتیبانی نمی شود. لطفا WAV, MP3, FLAC, OGG یا WEBM ارسال کنید.")

    # ذخیره موقت فایل صوتی
    file_extension = os.path.splitext(audio_file.filename)[1]
    temp_audio_path = f"temp_audio_{uuid.uuid4().hex}{file_extension}"
    
    try:
        with open(temp_audio_path, "wb") as buffer:
            while True:
                chunk = await audio_file.read(1024 * 1024) # 1MB chunks
                if not chunk:
                    break
                buffer.write(chunk)
        
        print(f"Received audio file saved temporarily at: {temp_audio_path}")

        # تبدیل گفتار به متن با استفاده از Whisper
        transcribed_text = transcribe_audio_file(temp_audio_path, language=language, task=task)
        print(f"Transcribed Text: {transcribed_text}")

        if "Error:" in transcribed_text:
            raise HTTPException(status_code=500, detail=f"خطا در تبدیل گفتار به متن: {transcribed_text}")

        # بازگرداندن پاسخ نهایی: فقط متن تبدیل شده
        # توجه: در جاوااسکریپت UI، این متن سپس به endpoint /chat/ ارسال می شود.
        return JSONResponse(content={
            "transcribed_text": transcribed_text
        })

    except Exception as e:
        print(f"Error processing audio: {e}")
        raise HTTPException(status_code=500, detail=f"خطای داخلی سرور در پردازش فایل صوتی: {str(e)}")
    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
            print(f"Temporary audio file removed: {temp_audio_path}")