from kokoro import KPipeline
import soundfile as sf
from pathlib import Path

def synthesize_speech(text: str, output_dir: Path, file_name: str = "output.wav", voice: str = 'af_heart'):
    pipeline = KPipeline(lang_code='a')
    generator = pipeline(text, voice=voice)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for i, (gs, ps, audio) in enumerate(generator):
        output_path = output_dir / file_name
        sf.write(output_path, audio, 24000)
        print(f"Saved audio to: {output_path}")
        break

    return str(output_path)