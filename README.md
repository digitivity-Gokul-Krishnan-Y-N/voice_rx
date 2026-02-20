# Medical Prescription Extraction System

A production-grade multilingual medical consultation transcription and prescription extraction system using OpenAI/local Whisper and Groq LLM APIs.

## 🎯 Features

- **Multilingual Audio Transcription**: Handles English, Tamil, and Thanglish with automatic language detection
- **Advanced Prescription Extraction**: Extracts patient name, complaints, diagnoses, medicines, tests, and advice
- **Groq LLM Integration**: Uses Groq's fast open-source models for intelligent data extraction
- **Intelligent Routing**: Quality-based routing between Groq extraction and rule-based fallback
- **Validation Layer**: Comprehensive validation with error and warning reporting
- **Database Storage**: SQLite integration for prescription persistence
- **Metrics Collection**: Performance tracking and quality metrics

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Medical System V2                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌─────────────────────────────────────┐
        │  [1] Audio Transcription            │
        │      (Whisper - local/OpenAI)       │
        └─────────────────────────────────────┘
                            ↓
        ┌─────────────────────────────────────┐
        │  [2] Transcript Cleaning            │
        │      (ASR distortion fixes)         │
        └─────────────────────────────────────┘
                            ↓
        ┌─────────────────────────────────────┐
        │  [3] Language Detection             │
        │      (EN/TA/Thanglish)              │
        └─────────────────────────────────────┘
                            ↓
        ┌─────────────────────────────────────┐
        │  [4] Thanglish Normalization        │
        │      (if needed)                    │
        └─────────────────────────────────────┘
                            ↓
        ┌─────────────────────────────────────┐
        │  [5] Transcript Normalization       │
        │      (dosage standardization)       │
        └─────────────────────────────────────┘
                            ↓
        ┌─────────────────────────────────────┐
        │  [6] Intelligent Routing            │
        ├─────────────────────────────────────┤
        │  ✓ Groq Extraction (primary)        │
        │  ✗ Rules-based Extraction (fallback)│
        └─────────────────────────────────────┘
                            ↓
        ┌─────────────────────────────────────┐
        │  [7] Validation & Storage           │
        │      (SQLite database)              │
        └─────────────────────────────────────┘
```

## 📦 Installation

### Prerequisites
- Python 3.9+
- FFmpeg (for audio processing)
- GPU optional (faster Whisper inference)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/digitivity-Gokul-Krishnan-Y-N/voice_rx.git
cd voice_rx
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
source venv/bin/activate      # Unix/macOS
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp config/.env.example config/.env
# Edit config/.env and add your API keys:
# GROQ_API_KEY=your_groq_api_key
# OPENAI_API_KEY=your_openai_api_key (optional, if using OpenAI Whisper)
```

## 🚀 Usage

### Basic Usage

```bash
python run_system.py
```

This will:
1. Transcribe `data/Thanglish.mp3` (or configured audio file)
2. Extract prescription data using Groq
3. Validate the extraction
4. Save results to `data/prescriptions.db`
5. Output JSON to console

### Configuration

Edit `src/medical_system_v2.py`:

```python
# Transcription source
WHISPER_MODEL = "medium"           # or "whisper-1" for OpenAI
TRANSCRIBER_SOURCE = "local"       # or "openai"

# Audio files to process
AUDIO_FILES = ["data/Thanglish.mp3"]

# Database
DB_FILE = "data/prescriptions.db"
```

### Example Output

```json
{
  "patient_name": "Rohit",
  "complaints": ["fever", "throat pain"],
  "diagnosis": ["acute pharyngitis", "bacterial infection"],
  "medicines": [
    {
      "name": "erythromycin",
      "dose": "500 mg",
      "frequency": "3 times a day",
      "duration": "5 days",
      "instruction": "after food"
    }
  ],
  "tests": [],
  "advice": [
    "Complete the full course of antibiotics",
    "Drink plenty of warm fluids",
    "Do warm salt water gargles 3-4 times a day"
  ]
}
```

## 📂 Project Structure

```
voice_rx/
├── src/
│   ├── medical_system_v2.py      # Main system orchestration
│   ├── transcription.py          # Whisper integration
│   ├── extraction.py             # Groq LLM extraction
│   ├── validation.py             # Prescription validation
│   ├── normalization.py          # Text normalization
│   ├── language_detection.py     # Language identification
│   ├── thanglish_normalizer.py   # Thanglish→Tamil conversion
│   ├── routing.py                # Quality-based routing
│   ├── metrics.py                # Performance metrics
│   ├── medicine_database.py      # Medicine validation DB
│   └── __pycache__/
│
├── config/
│   ├── .env                      # Environment variables (secrets)
│   ├── .env.example              # Example env template
│   └── medicine_db.json          # Medicine reference database
│
├── data/
│   ├── Thanglish.mp3             # Test audio file
│   └── prescriptions.db          # SQLite database (created after first run)
│
├── tests/
│   └── test_medical_system.py    # Unit and integration tests
│
├── docs/
│   ├── ARCHITECTURE_SUMMARY.md   # System design details
│   └── QUICK_REFERENCE.md        # API reference
│
├── frontend/
│   └── index.html                # Web UI (optional)
│
├── run_system.py                 # Main entry point
├── smart_labeling.py             # Smart text classification
├── README.md                     # This file
└── requirements.txt              # Python dependencies
```

## 🔧 Core Components

### Transcription (`src/transcription.py`)
- **WhisperTranscriber**: OpenAI Whisper API or local Whisper model
- **TranscriptCleaner**: Fixes ASR distortions (inflection→infection, etc.)
- Supports multilingual audio (English, Tamil, Thanglish)

### Extraction (`src/extraction.py`)
- **GroqLLMExtractor**: Primary extraction using Groq API
  - Temperature: 0 (deterministic)
  - max_tokens: 2000 (handles complete responses)
  - Automatic retry on parse failure
  - Robust JSON parsing with 4-level fallback strategy
  - Falls back to rules-based extraction if Groq fails

### Validation (`src/validation.py`)
- **ValidationLayer**: Validates extracted prescription data
- Checks for required fields (at least 1 medicine)
- Validates medicine names against database
- Detects dangerous drug combinations
- Returns detailed error/warning messages

### Routing (`src/routing.py`)
- **AudioAnalyzer**: Analyzes transcription quality
- **RouteSelector**: Routes between Groq (primary) and rules-based (fallback)
- Quality metrics: word density, medical keywords, confidence, length

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_medical_system.py -v

# Run with coverage
python -m pytest tests/ --cov=src
```

## 🔒 Security & Best Practices

- **API Keys**: Store in `config/.env`, never commit to git
- **Database**: SQLite is local; use PostgreSQL in production
- **Logging**: Check `medical_system_v2.log` for debugging
- **Rate Limiting**: Implement request throttling for Groq API in production
- **Input Validation**: All extracted data is validated before storage

## 📊 Performance Notes

### Transcription
- **Local Whisper (medium)**: ~15-30s per minute of audio (GPU faster)
- **OpenAI Whisper API**: ~5-10s per minute (cloud-based)

### Extraction
- **Groq**: ~2-3s (very fast, open-source models)
- **Rules-based**: <1s (instant, but less accurate)

### Total Processing Time
- For 90-second medical consultation: ~30-40s (with local Whisper)

## 🐛 Troubleshooting

### Groq extraction returning 0 medicines
- Check that transcript contains "medicine" keyword
- Increase max_tokens in `_extract_groq()` (currently 2000)
- Check Groq API status (openai/gpt-oss-120b model availability)

### Transcription quality issues
- Use longer audio files (>30 seconds for better detection)
- Ensure clear audio without background noise
- For Thanglish: model will auto-detect and normalize

### "At least one medicine required" validation error
- Medicine extraction needs explicit medicine mention in transcript
- Try: "Prescribe erythromycin 500 mg 3 times a day for 5 days"
- Check extraction logs for details

## 📝 API Reference

### MedicalSystem

```python
from src.medical_system_v2 import MedicalSystem

system = MedicalSystem()
result = system.process(audio_path="data/Thanglish.mp3")

# Result structure:
{
    "success": True,
    "patient_name": str,
    "complaints": List[str],
    "diagnosis": List[str],
    "medicines": List[Dict],
    "tests": List[str],
    "advice": List[str],
    "language": str,
    "confidence": float,
    "extraction_method": str,  # "groq" or "rules"
    "processing_time_sec": float,
    "route": str  # "groq_only" or "rules_fallback"
}
```

## 🚀 Future Enhancements

- [ ] Web API with FastAPI/Flask
- [ ] Batch processing for multiple audio files
- [ ] Custom medicine database per region
- [ ] Multi-language support (Spanish, French, etc.)
- [ ] Voice of the patient integration
- [ ] Doctor review interface
- [ ] Real-time transcription
- [ ] Mobile app integration

## 📜 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository: [voice_rx](https://github.com/digitivity-Gokul-Krishnan-Y-N/voice_rx)
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Support

For issues and questions:
- Create a GitHub Issue: [issues](https://github.com/digitivity-Gokul-Krishnan-Y-N/voice_rx/issues)
- Email: gokul.krishnan@digitivitysolutions.com

## 🙏 Acknowledgments

- OpenAI Whisper for multilingual transcription
- Groq for fast LLM inference
- The medical consultation dataset creators

---

**Last Updated**: February 2026  
**Version**: 2.0-Production  
**Status**: ✅ Production Ready
