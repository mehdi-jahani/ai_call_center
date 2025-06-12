from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api_interface.routes import router as api_router
from chat_interface.web_chat import router as chat_ui_router

app = FastAPI()

# مسیر UI چت
app.include_router(chat_ui_router, prefix="/chat")

# مسیرهای API
app.include_router(api_router)

# این خطوط برای سرویس‌دهی فایل‌های استاتیک ضروری هستند.
# اطمینان حاصل کنید که پوشه 'data' در سطح ریشه پروژه شما (کنار main.py) وجود دارد
# و تصاویر شما در 'data/images' قرار گرفته‌اند.
app.mount("/static", StaticFiles(directory="data"), name="static")

@app.get("/")
def root():
    """
    مسیر اصلی برنامه FastAPI.
    """
    return {"message": "AI Call Center is running"}