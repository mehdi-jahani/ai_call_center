from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates # <--- این خط را اضافه کنید

# تنظیم مسیر پوشه قالب ها
# فرض می کنیم پوشه 'templates' در کنار 'web_chat.py' قرار دارد، یعنی:
# ai_call_center/
# ├── chat_interface/
# │   ├── templates/
# │   │   └── chat.html
# │   └── web_chat.py
# └── ...
templates = Jinja2Templates(directory="chat_interface/templates")

router = APIRouter()

@router.get("/ui", response_class=HTMLResponse)
async def chat_ui(request: Request):
    """
    مسیر GET برای نمایش رابط کاربری چت.
    این تابع فایل 'chat.html' را رندر کرده و به مرورگر ارسال می کند.
    """
    return templates.TemplateResponse("chat.html", {"request": request})

@router.post("/") # <--- این مسیر در main.py با prefix="/chat" اضافه می شود، پس آدرس کامل /chat/ می شود
async def chat_endpoint(request: Request):
    """
    مسیر POST برای دریافت پیام های چت از رابط کاربری و تولید پاسخ.
    """
    try:
        data = await request.json()
        user_message = data.get("text") # نام فیلد در JS شما "text" است

        if not user_message:
            return {"reply": "Please enter a message."}

        from nlp_engine.response_generator import generate_response

        bot_response_html = generate_response(user_message)

        return {"reply": bot_response_html}
    except Exception as e:
        print(f"Error in chat_endpoint: {e}")
        return {"reply": "An error occurred while processing your message."}