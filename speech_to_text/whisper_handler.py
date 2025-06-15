import torch
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
import soundfile as sf
import librosa
import os
import io

# Whisper model name
WHISPER_MODEL_NAME = "openai/whisper-medium" 

# Global variables to store the processor and model
# These are loaded only once to prevent reloading on every request
processor = None
model = None
device = None # For storing the active device (cuda or cpu)

def load_whisper_model():
    """
    Loads the Whisper model and its processor.
    This function should only be called once when the program starts (e.g., in main.py).
    """
    global processor, model, device

    if processor is not None and model is not None:
        print("Whisper model already loaded.")
        return

    print(f"Loading Whisper model: {WHISPER_MODEL_NAME}...")
    try:
        # Determine device for model loading (cuda for GPU, cpu for CPU)
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        # Load processor and model from Hugging Face
        processor = AutoProcessor.from_pretrained(WHISPER_MODEL_NAME)
        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            WHISPER_MODEL_NAME,
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True
        ).to(device)

        model.eval()

        print(f"Whisper model loaded successfully on device: {device}")
    except Exception as e:
        print(f"Error loading Whisper model: {e}")
        processor = None
        model = None
        device = None

def transcribe_audio_file(audio_path: str, language: str = "persian", task: str = "transcribe") -> str:
    """
    Converts an audio file to text.
    The audio file should be in .flac, .wav, .mp3, or other formats supported by librosa.
    Args:
        audio_path (str): Path to the audio file.
        language (str): Expected output language (e.g., "english", "persian", "french").
                       Used for multilingual models.
                       Check Whisper documentation for supported languages.
        task (str): Desired task ("transcribe" for speech-to-text, "translate" for translation to English).
    Returns:
        str: Transcribed text from the audio file.
    """
    global processor, model, device

    if processor is None or model is None or device is None:
        load_whisper_model()
        if processor is None or model is None or device is None:
            return "Error: Speech-to-Text model not loaded. Cannot transcribe audio."

    try:
        audio_input, sampling_rate = librosa.load(audio_path, sr=None)

        if sampling_rate != 16000:
            print(f"Resampling audio from {sampling_rate} Hz to 16000 Hz...")
            audio_input = librosa.resample(audio_input, orig_sr=sampling_rate, target_sr=16000)
            sampling_rate = 16000

        input_features = processor(
            audio_input,
            sampling_rate=sampling_rate,
            return_tensors="pt"
        ).input_features.to(device)

        forced_decoder_ids = processor.get_decoder_prompt_ids(
            language=language,
            task=task,
            no_timestamps=True
        )
        
        # Generate output tokens (the text)
        generated_ids = model.generate(
            input_features=input_features,
            forced_decoder_ids=forced_decoder_ids,
            max_new_tokens=256,
        )

        # Decode tokens to readable text
        # skip_special_tokens=True to remove context tokens like <|startoftranscript|>
        transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return transcription.strip()

    except FileNotFoundError:
        return "Error: Audio file not found at the specified path."
    except Exception as e:
        print(f"Error during audio transcription: {e}")
        return f"An unexpected error occurred during audio transcription: {e}"

# Example usage (for testing)
if __name__ == "__main__":

    load_whisper_model()

    audio_file_to_transcribe = "test.wav"

    if os.path.exists(audio_file_to_transcribe):
        print(f"\nTranscribing '{audio_file_to_transcribe}' (Language: Persian)...")
        transcribed_text = transcribe_audio_file(audio_file_to_transcribe, language="persian")
        print(f"Transcribed Text: {transcribed_text}")
    else:
        print(f"\nError: Test audio file not found at {audio_file_to_transcribe}.")
        print("Please create or place a 16kHz WAV/MP3 file named 'test_persian.wav' in your project root for testing.")
        print("You can also uncomment the dummy audio generation code if you install 'numpy' and 'scipy'.")