from fastapi import APIRouter
from pydantic import BaseModel
# Assuming nlp_engine is a package and response_generator is a module inside it
from nlp_engine.response_generator import generate_response # <--- ADD THIS LINE

router = APIRouter()

class MessageInput(BaseModel):
    text: str
    source: str  # chat | voice
    lang: str = "en"

@router.post("/chat")
def chat_response(data: MessageInput):
    # اتصال به NLP و پاسخ‌دهی
    # Use the generate_response function
    reply_text = generate_response(data.text) # <--- MODIFIED LINE
    return {"reply": reply_text} # <--- MODIFIED LINE