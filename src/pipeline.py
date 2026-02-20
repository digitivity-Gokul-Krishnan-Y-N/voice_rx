import os
import sys
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Load .env from config folder (correct path)
config_path = Path(__file__).parent.parent / 'config' / '.env'
print(f"Loading config from: {config_path}")
load_dotenv(config_path)

# Check for API key
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print("ERROR: OPENAI_API_KEY not found")
    sys.exit(1)

client = OpenAI(api_key=api_key)

AUDIO_FILES = ["data\WhatsApp Audio 2026-02-20 at 12.36.29 PM.mp4"]

SYSTEM_PROMPT = """
You are a medical documentation assistant.

Your task:
- Extract structured prescription data from doctor speech.

Rules:
- Output ONLY valid JSON
- Do NOT invent data
- Use standard medical names
- If information is missing, return empty lists
- Do NOT add explanations or extra text

Return JSON with EXACTLY these keys:
patient_name (string or null)
complaints (array of strings)
diagnosis (array of strings)
medicines (array of objects with name, dose, frequency, duration)
tests (array of strings)
advice (array of strings)
"""

def transcribe_audio():
    print("[TRANSCRIBING] Processing audio files...")
    full_transcript = ""
    
    for audio_file in AUDIO_FILES:
        # Resolve path relative to project root
        audio_path = Path(__file__).parent.parent / audio_file.replace("\\", "/")
        
        if not audio_path.exists():
            print(f"[ERROR] File not found: {audio_path}")
            continue
            
        print(f"  Processing: {audio_path}")
        with open(audio_path, "rb") as audio:
            transcript = client.audio.transcriptions.create(
                file=audio,
                model="whisper-1",
                language="en"
            )
        full_transcript += transcript.text + " "
    
    print("[TRANSCRIPT] Combined output:")
    print(full_transcript if full_transcript else "[WARNING] No transcript generated")
    return full_transcript


def extract_prescription(transcript_text):
    print("\n[EXTRACTING] Processing prescription data...")
    
    if not transcript_text or not transcript_text.strip():
        print("[ERROR] Empty transcript - cannot extract prescription")
        return None

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": transcript_text}
        ],
        temperature=0
    )

    raw_output = response.choices[0].message.content

    try:
        rx_data = json.loads(raw_output)
        print("\n[SUCCESS] Structured Prescription JSON:\n")
        print(json.dumps(rx_data, indent=2))
        return rx_data
    except json.JSONDecodeError:
        print("\n[ERROR] Invalid JSON returned:\n")
        print(raw_output)
        return None


if __name__ == "__main__":
    transcript = transcribe_audio()
    extract_prescription(transcript)