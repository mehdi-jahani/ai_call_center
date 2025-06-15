from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import uuid

# Import functions from Whisper module
from speech_to_text.whisper_handler import transcribe_audio_file
from nlp_engine.response_generator import generate_response 

router = APIRouter()

# Define temporary directory path for audio files
# This path should be set as absolute or relative to project root
TEMP_AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'temp_audio_files')

# Model for text chat message input
class MessageInput(BaseModel):
    text: str
    source: str  # chat | voice
    lang: str = "en"

# An endpoint for initial API connection test
@router.get("/api/health")
async def api_health_check():
    """
    Check API health.
    """
    return {"status": "ok", "message": "API is healthy"}

# Route for receiving text message (from chat UI or after voice conversion)
@router.post("/chat")
def chat_response(data: MessageInput):
    """
    Receives text message and sends it to NLP engine to generate response.
    """
    print(f"Received text message from {data.source}: {data.text}")
    reply_text = generate_response(data.text)
    print(f"Generated NLP reply: {reply_text}")
    return {"reply": reply_text}

# Route for receiving audio file and converting it to text
@router.post("/api/process_audio")
async def process_audio_endpoint(
    audio_file: UploadFile = File(..., description="Audio file for processing (WAV, MP3, FLAC, OGG, WEBM)"),
    language: str = Form("persian", description="Audio file language (e.g., 'persian', 'english')"),
    task: str = Form("transcribe", description="Whisper task ('transcribe' or 'translate')")
):
    """
    Receives an audio file and converts it to text.
    Returns the transcribed text as JSON.
    """
    if not audio_file.filename.lower().endswith(('.wav', '.mp3', '.flac', '.ogg', '.webm')):
        raise HTTPException(status_code=400, detail="Unsupported audio file format. Please send WAV, MP3, FLAC, OGG, or WEBM.")

    # Temporarily save audio file in TEMP_AUDIO_DIR
    file_extension = os.path.splitext(audio_file.filename)[1]
    # Create complete temporary file path
    temp_audio_path = os.path.join(TEMP_AUDIO_DIR, f"temp_audio_{uuid.uuid4().hex}{file_extension}")
    
    try:
        with open(temp_audio_path, "wb") as buffer:
            while True:
                chunk = await audio_file.read(1024 * 1024) # 1MB chunks
                if not chunk:
                    break
                buffer.write(chunk)
        
        print(f"Received audio file saved temporarily at: {temp_audio_path}")

        # Convert speech to text using Whisper
        transcribed_text = transcribe_audio_file(temp_audio_path, language=language, task=task)
        print(f"Transcribed Text: {transcribed_text}")

        if "Error:" in transcribed_text:
            raise HTTPException(status_code=500, detail=f"Error in speech-to-text conversion: {transcribed_text}")

        return JSONResponse(content={
            "transcribed_text": transcribed_text
        })

    except Exception as e:
        print(f"Error processing audio: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error in audio file processing: {str(e)}")
    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
            print(f"Temporary audio file removed: {temp_audio_path}")