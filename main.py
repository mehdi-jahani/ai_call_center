from fastapi import FastAPI
from api_interface.routes import router as api_router
from chat_interface.web_chat import router as chat_ui_router

app = FastAPI()

# مسیر UI چت
app.include_router(chat_ui_router, prefix="/chat")

# مسیرهای API
app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "AI Call Center is running"}
