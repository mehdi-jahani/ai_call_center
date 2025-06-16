from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api_interface.routes import router as api_router
from chat_interface.web_chat import router as chat_ui_router
from speech_to_text.whisper_handler import load_whisper_model
import os
from api_interface.routes import TEMP_AUDIO_DIR
import logging

# پیکربندی اولیه لاگینگ
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
LOG_FILE_PATH = os.path.join(LOG_DIR, 'app.log')

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()

# مسیر UI چت
app.include_router(chat_ui_router, prefix="/chat")

# مسیرهای API
app.include_router(api_router)

# -- نکته: mount دقیق‌تر (audio) باید قبل از mount کلی‌تر (static) بیاید --
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # مسیر اصلی پروژه
AUDIO_DIR = os.path.join(BASE_DIR, "outputs", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)
app.mount("/static/audio", StaticFiles(directory=AUDIO_DIR), name="audio")    # اول mount کن
app.mount("/static", StaticFiles(directory="data"), name="static")            # بعد mount کن

@app.on_event("startup")
async def startup_event():
    """
    این تابع در زمان شروع برنامه اجرا می‌شود.
    مدل های LLM و Whisper را بارگذاری می کند و پوشه فایل های موقت را ایجاد می کند.
    """
    logger.info("Application startup event: Loading all necessary AI models and setting up directories...")
    load_whisper_model()

    # ایجاد پوشه موقت اگر وجود نداشته باشد
    if not os.path.exists(TEMP_AUDIO_DIR):
        os.makedirs(TEMP_AUDIO_DIR)
        logger.info(f"Created temporary audio directory: {TEMP_AUDIO_DIR}")
    else:
        logger.info(f"Temporary audio directory already exists: {TEMP_AUDIO_DIR}")

@app.get("/")
def root():
    """
    مسیر اصلی برنامه FastAPI.
    """
    logger.info("Root endpoint accessed.")
    return {"message": "AI Call Center is running"}