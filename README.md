# Voice RX - AI Medical Prescription System

An advanced AI-powered medical prescription extraction system that converts doctor-patient consultations from audio (speech) into structured, validated prescriptions using Whisper ASR and rule-based extraction.

## Features

✅ **Speech-to-Text Transcription**
- Whisper ASR (base model) for accurate audio transcription
- Automatic language detection (English, Tamil, Telugu support)
- Audio preprocessing and normalization

✅ **Smart Prescription Extraction**
- Patient name recognition
- Diagnosis extraction with context awareness
- Medicine identification with dosage, frequency, and duration
- Complaint/symptom extraction
- Medical advice generation (12 standard phrases)
- Test/investigation recommendations

✅ **Medical Database**
- 100+ medicines across 12 categories
- Drug interaction warnings
- Dangerous combination detection
- Transcription error corrections (50+ patterns)

✅ **Validation & Safety**
- Prescription validation (required fields, dose formats)
- Drug interaction checking
- Duplicate medicine detection
- Safety warnings and alerts

✅ **Database Persistence**
- SQLite database for prescription storage
- Structured data models (Prescription, Medicine, Patient)
- Audit trail with timestamps

✅ **Multi-lingual Support**
- English transcription
- Tanglish/Transliteration handling
- Language auto-detection with fallback

## System Architecture

```
┌─────────────────────────────────────┐
│  Audio Input (MP3/WAV)              │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│  Speech Recognition (Whisper)        │
│  - Audio preprocessing               │
│  - Language detection                │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│  Extraction Engine                   │
│  - Patient name extraction           │
│  - Diagnosis extraction              │
│  - Medicine extraction               │
│  - Advice generation                 │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│  Validation Layer                    │
│  - Format validation                 │
│  - Drug interaction check            │
│  - Safety warnings                   │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│  Database Storage (SQLite)           │
│  - Prescription persistence          │
│  - Audit trail                       │
└─────────────────────────────────────┘
```

## Project Structure

```
voice_rx/
├── medical_system_v2.py          # Main system orchestrator
├── medicine_database.py          # Medicine database & configurations
├── pipeline.py                   # Alternative pipeline (GPT-4 based)
├── doctor_review.py              # Doctor review UI module
├── enhanced_validation.py         # Enhanced prescription validation
├── monitoring.py                 # System monitoring & metrics
├── smart_labeling.py             # Smart text classification
├── requirements.txt              # Python dependencies
├── prescriptions.db              # SQLite database
├── frontend/                     # Web interface (HTML/CSS/JS)
├── venv/                         # Python virtual environment
└── README.md                     # This file
```

## Installation

### Prerequisites
- Python 3.8+
- FFmpeg (for audio processing)
- Git

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/digitivity-Gokul-Krishnan-Y-N/voice_rx.git
cd voice_rx
```

2. **Create virtual environment:**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Download Whisper model:**
```bash
python -c "import whisper; whisper.load_model('base')"
```

## Usage

### Run Medical System V2
```bash
python medical_system_v2.py
```

This will:
- Load the audio file (WhatsApp.mp3)
- Transcribe the consultation
- Extract prescription data
- Validate against medical database
- Save to SQLite database
- Output JSON prescription

### Example Output

```json
{
  "patient_name": "Rogit",
  "complaints": ["throat pain", "fever", "infection"],
  "diagnosis": ["bacterial throat infection", "acute pharyngitis"],
  "medicines": [
    {
      "name": "Erythromycin",
      "dose": "500 mg",
      "frequency": "3 times a day",
      "duration": "5 days"
    }
  ],
  "advice": [
    "Take erythromycin after food to avoid stomach discomfort",
    "Complete the full 5 day course of antibiotics",
    "Drink plenty of warm fluids",
    "Do warm salt water gargles 3-4 times a day",
    "Rest your voice as much as possible",
    ...
  ],
  "tests": []
}
```

## Configuration

### Medicine Database

Edit `medicine_database.py` to:
- Add/remove medicines to `KNOWN_DRUGS`
- Add drug interactions to `DANGEROUS_COMBINATIONS`
- Update medical term corrections in `DRUG_CORRECTIONS`
- Modify standard advice phrases in `STANDARD_ADVICE`

### Extraction Rules

Modify `medical_system_v2.py`:
- `_extract_medicines()` - Medicine pattern matching
- `_extract_complaints()` - Symptom detection
- `_extract_diagnosis()` - Diagnosis mapping
- `_extract_from_keywords()` - Advice generation

## Performance

| Model | Speed | Accuracy | Memory |
|-------|-------|----------|--------|
| tiny | ~5s | 70% | 39MB |
| base | ~20s | 85% | 140MB |
| small | ~60s | 90% | 480MB |
| medium | ~2min | 95% | 1.4GB |

**Current:** Base model on CPU (~20 seconds per consultation)

## Database Schema

### prescriptions table
- `id` (INTEGER PRIMARY KEY)
- `patient_name` (TEXT)
- `diagnosis` (TEXT JSON)
- `medicines` (TEXT JSON)
- `advice` (TEXT JSON)
- `tests` (TEXT JSON)
- `timestamp` (DATETIME)
- `confidence` (FLOAT)

## Dependencies

- `whisper` - Speech recognition
- `librosa` - Audio processing
- `numpy`, `scipy` - Numerical computation
- `sqlite3` - Database (built-in)
- `regex` - Pattern matching
- `python-dotenv` - Environment variables

See `requirements.txt` for complete list.

## Troubleshooting

### Issue: "Whisper model not found"
```bash
python -c "import whisper; whisper.load_model('base')"
```

### Issue: "Medicine database module not available"
Ensure `medicine_database.py` is in the same directory as `medical_system_v2.py`

### Issue: Audio file not found
Place your audio file (MP3/WAV) in the working directory and update `AUDIO_FILES` in the config.

## Module Descriptions

### medical_system_v2.py
Main orchestrator that:
- Loads and transcribes audio
- Extracts prescription data
- Validates prescriptions
- Stores to database
- Generates JSON output

### medicine_database.py
Centralized data repository containing:
- Drug inventory (100+ medicines)
- Drug interactions
- Transcription corrections
- Standard medical advice
- Extraction keywords

### doctor_review.py
UI module for:
- Doctor approval/modification
- Quality verification
- Correction workflow

### enhanced_validation.py
Advanced validation:
- Dosage verification
- Drug interaction checking
- Medical guideline compliance

### monitoring.py
System observability:
- Performance metrics
- Error tracking
- System health

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Future Enhancements

- [ ] Multi-language full support
- [ ] OCR for prescription images
- [ ] Real-time audio streaming
- [ ] ML-based extraction instead of rule-based
- [ ] Web dashboard for doctor interface
- [ ] Mobile app integration
- [ ] Insurance claim generation
- [ ] Automated follow-up scheduling

## License

This project is proprietary software by Digitivity. Unauthorized copying or distribution is prohibited.

## Contact

- **GitHub:** https://github.com/digitivity-Gokul-Krishnan-Y-N
- **Repository:** https://github.com/digitivity-Gokul-Krishnan-Y-N/voice_rx

## Changelog

### v2.1 (Current)
- ✅ Fine-tuned extraction methods
- ✅ Expanded medicine database (100+ drugs)
- ✅ Separated medicine database module
- ✅ Improved complaint/diagnosis prioritization
- ✅ Enhanced medical term corrections

### v2.0
- ✅ Core prescription extraction
- ✅ Whisper ASR integration
- ✅ SQLite persistence
- ✅ Validation layer

### v1.0
- Initial release

---

**Last Updated:** 2026-02-18  
**Status:** ✅ Production Ready
