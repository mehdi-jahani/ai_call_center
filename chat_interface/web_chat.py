from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from nlp_engine.response_generator import generate_response
from text_to_speech.kokoro_handler import synthesize_speech
from pathlib import Path
from bs4 import BeautifulSoup
import uuid
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
AUDIO_DIR = os.path.join(PROJECT_ROOT, "outputs", "audio")

templates = Jinja2Templates(directory="chat_interface/templates")
router = APIRouter()

def extract_tts_text(bot_response_text: str) -> str:
    """
    اگر پیام شامل کارت محصول بود، عنوان و قیمت محصول اصلی و محصولات مرتبط را برای TTS استخراج می‌کند.
    اگر نبود همان متن را بازمی‌گرداند.
    """
    if 'div class' in bot_response_text:
        soup = BeautifulSoup(bot_response_text, "html.parser")
        # محصول اصلی
        title_tag = soup.find("a", class_="product-title-link")
        title = title_tag.get_text(strip=True) if title_tag else "Product"
        price_tag = soup.find("p", class_="product-price")
        price = price_tag.get_text(strip=True).replace("$", "") if price_tag else ""
        summary = f"{title}"
        if price:
            summary += f", price {price} dollars."

        # محصولات مرتبط (فقط 2 عدد برای کوتاه‌تر شدن صوت)
        related_products = []
        rel_items = soup.select('.product-list .product-item')
        for item in rel_items[:2]:
            rel_title_tag = item.find("a", class_="product-item-title")
            rel_title = rel_title_tag.get_text(strip=True) if rel_title_tag else ""
            rel_price_tag = item.find("p", class_="product-item-price")
            rel_price = rel_price_tag.get_text(strip=True).replace("$", "") if rel_price_tag else ""
            if rel_title:
                txt = rel_title
                if rel_price:
                    txt += f", price {rel_price} dollars"
                related_products.append(txt)
        if related_products:
            summary += " Related products: " + "; ".join(related_products) + "."

        return summary

    return bot_response_text

@router.get("/ui", response_class=HTMLResponse)
async def chat_ui(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@router.post("/")
async def chat_endpoint(request: Request):
    try:
        data = await request.json()
        user_message = data.get("text")

        if not user_message:
            return {"reply": "Please enter a message."}

        bot_response_text = generate_response(user_message)
        tts_text = extract_tts_text(bot_response_text)

        os.makedirs(AUDIO_DIR, exist_ok=True)
        audio_filename = f"{uuid.uuid4().hex}.wav"
        audio_output_dir = Path(AUDIO_DIR)
        audio_path = synthesize_speech(tts_text, audio_output_dir, file_name=audio_filename)
        audio_url = f"/static/audio/{audio_filename}"

        return {
            "reply": bot_response_text,
            "reply_audio_url": audio_url
        }
    except Exception as e:
        print(f"Error in chat_endpoint: {e}")
        return {"reply": "An error occurred while processing your message."}