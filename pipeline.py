import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

AUDIO_FILES = ["WhatsApp.mp3"]

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
    print("🎧 Transcribing audio files...")
    full_transcript = ""
    
    for audio_file in AUDIO_FILES:
        if not os.path.exists(audio_file):
            print(f"⚠️  File not found: {audio_file}")
            continue
            
        print(f"  Processing: {audio_file}")
        with open(audio_file, "rb") as audio:
            transcript = client.audio.transcriptions.create(
                file=audio,
                model="whisper-1",
                language="en"
            )
        full_transcript += transcript.text + " "
    
    print("📝 Combined Transcript:")
    print(full_transcript)
    return full_transcript


def extract_prescription(transcript_text):
    print("\n🧠 Extracting prescription data...")

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
        print("\n✅ Structured Prescription JSON:\n")
        print(json.dumps(rx_data, indent=2))
        return rx_data
    except json.JSONDecodeError:
        print("\n❌ Invalid JSON returned:\n")
        print(raw_output)
        return None


if __name__ == "__main__":
    transcript = transcribe_audio()
    extract_prescription(transcript)