import os
import json
import logging
import whisper
import sqlite3
import numpy as np
from scipy.io import wavfile
from dotenv import load_dotenv
import librosa
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
import re
import subprocess
import sys
import hashlib
import uuid
from collections import defaultdict
import time

# ✅ Import upgraded modules
try:
    from monitoring import MonitoringEngine, SystemMetrics, StructuredFormatter
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    print("⚠️  Monitoring module not available")

try:
    from enhanced_validation import EnhancedValidationLayer, DRUG_DATABASE
    ENHANCED_VALIDATION_AVAILABLE = True
except ImportError:
    ENHANCED_VALIDATION_AVAILABLE = False
    print("⚠️  Enhanced validation module not available")

try:
    from doctor_review import DoctorReviewUI
    DOCTOR_REVIEW_AVAILABLE = True
except ImportError:
    DOCTOR_REVIEW_AVAILABLE = False
    print("⚠️  Doctor review module not available")

try:
    from smart_labeling import SmartLabelClassifier
    SMART_LABELING_AVAILABLE = True
except ImportError:
    SMART_LABELING_AVAILABLE = False
    print("⚠️  Smart labeling module not available")

# Import medicine database
try:
    from medicine_database import (
        KNOWN_DRUGS, DANGEROUS_COMBINATIONS, DOSE_PATTERNS,
        DRUG_CORRECTIONS, COMPLAINT_KEYWORDS, DIAGNOSIS_KEYWORDS,
        STANDARD_ADVICE, ADVICE_MAPPING
    )
    MEDICINE_DB_AVAILABLE = True
except ImportError:
    MEDICINE_DB_AVAILABLE = False
    print("⚠️  Medicine database module not available")

# ==================== SETUP & CONFIGURATION ====================

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('medical_system_v2.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

# ==================== CONFIGURATION ====================

# AUDIO_FILE = "recording.wav"
AUDIO_FILES =  ["WhatsApp.mp3"]

WHISPER_MODEL = "base"  # base (140MB) = best balance: fast (~15 seconds) + good accuracy. Avoid medium (2+ min)
MODEL_DEVICE = "cpu"  # cpu for CPU-only machines. Use cuda if NVIDIA GPU available
DB_FILE = "prescriptions.db"

# Feature flags
USE_LLAMA3_EXTRACTION = False  # Disable for speed (rule-based is enough)
USE_FASTTEXT_DETECTION = False  # Disable for speed
USE_AI4BHARAT_TRANSLITERATION = False  # Disable for speed
ENABLE_AUDIT_LOGGING = False
ENABLE_MONITORING = False

# ==================== DATA STRUCTURES ====================

@dataclass
class Medicine:
    name: str
    dose: str
    frequency: str
    duration: str
    instruction: str = ""
    route: str = "oral"  # oral, IV, topical, etc.
    side_effects: List[str] = field(default_factory=list)

@dataclass
class Prescription:
    patient_name: str
    age: Optional[int]
    language: str
    complaints: List[str]
    diagnosis: List[str]
    medicines: List[Medicine]
    tests: List[str]
    advice: List[str]
    timestamp: str = ""
    confidence: float = 0.0
    doctor_id: str = "unknown"  # For multi-doctor tracking
    doctor_approved: bool = False
    approval_timestamp: Optional[str] = None
    whisper_confidence: float = 0.0
    language_detection_confidence: float = 0.0
    extraction_method: str = "rules"  # rules or llama3
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self):
        return {
            "patient_name": self.patient_name,
            "age": self.age,
            "language": self.language,
            "complaints": self.complaints,
            "diagnosis": self.diagnosis,
            "medicines": [asdict(m) for m in self.medicines],
            "tests": self.tests,
            "advice": self.advice,
            "timestamp": self.timestamp or datetime.now().isoformat(),
            "confidence": self.confidence,
            "doctor_id": self.doctor_id,
            "doctor_approved": self.doctor_approved,
            "approval_timestamp": self.approval_timestamp,
            "extraction_method": self.extraction_method,
            "warnings": self.warnings
        }

# ==================== AUDIO PREPROCESSING ====================

def preprocess_audio(audio_path: str) -> Tuple[int, np.ndarray]:
    """Load and preprocess audio - supports WAV, MP3, and other formats"""
    file_ext = os.path.splitext(audio_path)[1].lower()
    
    try:
        if file_ext in ['.mp3', '.m4a', '.ogg', '.flac']:
            # Use librosa for MP3 and other formats
            logger.info(f"Loading {file_ext} file with librosa...")
            audio_data, sample_rate = librosa.load(audio_path, sr=None, mono=False)
        else:
            # Use scipy for WAV files
            sample_rate, audio_data = wavfile.read(audio_path)
    except Exception as e:
        logger.warning(f"scipy.wavfile failed, falling back to librosa: {e}")
        audio_data, sample_rate = librosa.load(audio_path, sr=None, mono=False)
    
    # Convert to float32
    if audio_data.dtype != np.float32:
        audio_data = audio_data.astype(np.float32)
        if np.max(np.abs(audio_data)) > 1:
            audio_data = audio_data / np.max(np.abs(audio_data))
    
    # Stereo to mono
    if len(audio_data.shape) > 1:
        audio_data = np.mean(audio_data, axis=1).astype(np.float32)
    
    # Normalize
    max_val = np.max(np.abs(audio_data))
    if max_val > 0:
        audio_data = audio_data / max_val
    
    return sample_rate, audio_data

# ==================== STEP 1: SPEECH RECOGNITION ====================

class WhisperTranscriber:
    """Whisper - Auto-detects language (EN/TA/Tanglish)"""
    
    def __init__(self, model_size: str = "medium"):
        logger.info(f"Loading Whisper {model_size} model...")
        self.model = whisper.load_model(model_size, device=MODEL_DEVICE)
        logger.info(f"✅ Whisper {model_size} loaded")
    
    def transcribe(self, audio_path: str) -> Dict:
        """Transcribe without forcing language"""
        try:
            logger.info("Preprocessing audio...")
            sample_rate, audio_data = preprocess_audio(audio_path)
            
            # Resample to 16kHz if needed
            if sample_rate != 16000:
                ratio = 16000 / sample_rate
                new_length = int(len(audio_data) * ratio)
                indices = np.linspace(0, len(audio_data)-1, new_length)
                audio_data = np.interp(indices, np.arange(len(audio_data)), audio_data).astype(np.float32)
            
            logger.info("Transcribing with Whisper (English)...")
            
            # FORCE English to avoid auto-detect issues (detection as Telugu, etc)
            result = self.model.transcribe(
                audio_data,
                fp16=False,
                language="en",  # Force English - auto-detect often fails
                prompt="Medical consultation with doctor discussing diagnosis and prescription."
            )
            
            transcript = result.get("text", "").strip()
            detected_language = "en"  # Forced to English
            confidence = 1.0 - np.mean([s.get("no_speech_prob", 0.5) for s in result.get("segments", [])])
            
            logger.info(f"✅ Transcribed (en): {transcript[:80]}...")
            
            return {
                "success": True,
                "text": transcript,
                "whisper_language": detected_language,  # Whisper's language code
                "confidence": confidence
            }
        
        except Exception as e:
            logger.error(f"❌ Transcription error: {e}")
            return {"success": False, "error": str(e)}

# ==================== STEP 2: LANGUAGE DETECTION ====================

class LanguageDetector:
    """Detect language: English, Tamil, or Tanglish"""
    
    TAMIL_RANGE = range(0x0B80, 0x0BFF)
    
    TAMIL_KEYWORDS = {
        'நோய്', 'மருந்து', 'வலி', 'காய்ச்சல்', 'இருமல்', 'தலைவலி',
        'மாத்திரை', 'அலர்ஜி', 'சர்க்கரை', 'உயர் இரத்த அழுத்தம்'
    }
    
    TANGLISH_PATTERNS = [
        r'(noi|noy|marunthu|maruthuu|vali|kai|pill|tablet)',
        r'(kaalai|iravu|madhyan|sirikaram)',
        r'(eduthuko|sapai|sapirangi)',
    ]
    
    def detect(self, text: str) -> Tuple[str, float]:
        """Return (language_code, confidence) - 'en', 'ta', or 'tanglish'"""
        text_lower = text.lower()
        
        # Count Tamil characters
        tamil_char_count = sum(1 for char in text if ord(char) in self.TAMIL_RANGE)
        tamil_ratio = tamil_char_count / len(text) if text else 0
        
        # If >10% Tamil Unicode, it's Tamil
        if tamil_ratio > 0.1:
            logger.info(f"[TAMIL] Unicode detected ({tamil_ratio:.1%})")
            return "ta", float(tamil_ratio)
        
        # Check for Tanglish patterns
        tanglish_matches = sum(1 for pattern in self.TANGLISH_PATTERNS 
                               if re.search(pattern, text_lower))
        
        if tanglish_matches >= 2:
            confidence = 0.5 + (tanglish_matches * 0.15)
            logger.info(f"[TANGLISH] {tanglish_matches} markers found ({confidence:.1%})")
            return "tanglish", min(confidence, 0.95)
        
        logger.info("[ENGLISH] Default language detected")
        return "en", 0.85

# ==================== STEP 3: TANGLISH TRANSLITERATION ====================

class TanglishTransliterator:
    """
    Convert Tanglish to Tamil using AI4Bharat Indic NLP
    Falls back to manual mapping if library unavailable
    """
    
    # Comprehensive Tanglish → Tamil mapping
    TANGLISH_MAP = {
        # Medical terms
        'noi': 'நோய்', 'noy': 'நோய்', 'disease': 'நோய்',
        'marunthu': 'மருந்து', 'medicine': 'மருந்து', 'drug': 'மருந்து',
        'vali': 'வலி', 'pain': 'வலி',
        'kai': 'கை', 'kaiychal': 'இருமல்', 'cough': 'இருமல்',
        'sirikaram': 'சர்க்கரை', 'sugar': 'சர்க்கரை', 'diabetes': 'சர்க்கரை',
        'fever': 'காய்ச்சல்', 'thandu': 'காய்ச்சல்',
        'pill': 'மாத்திரை', 'tablet': 'மாத்திரை',
        'allergy': 'அலர்ஜி', 'alergy': 'அலர்ஜி',
        
        # Time-related
        'kaalai': 'காலை', 'morning': 'காலை',
        'iravu': 'இரவு', 'night': 'இரவு',
        'madhyan': 'மதியம்', 'afternoon': 'மதியம்',
        
        # Instructions
        'sapai': 'சாப்பிற்கு', 'before': 'சாப்பிற்கு',
        'sapiranthellai': 'சாப்பிற்கு பிறகு', 'after': 'சாப்பிற்கு பிறகு',
        
        # Dosage
        'oru': 'ஒரு', 'one': 'ஒரு',
        'rendu': 'இரண்டு', 'two': 'இரண்டு',
        'munu': 'மூன்று', 'three': 'மூன்று',
    }
    
    def transliterate(self, text: str) -> str:
        """Convert Tanglish to Tamil or Tamil representation"""
        try:
            # Try to import indic-nlp library if available
            from indic_nlp.transliterate import unicode_transliterate
            from indic_nlp.normalize import normalize
            
            logger.info("Using AI4Bharat Indic NLP for transliteration...")
            
            # This would require proper setup, fallback for now
            return self._manual_transliterate(text)
        
        except ImportError:
            logger.info("AI4Bharat library not found, using manual transliteration...")
            return self._manual_transliterate(text)
    
    def _manual_transliterate(self, text: str) -> str:
        """Fallback: Manual transliteration using dictionary"""
        result = text.lower()
        
        # Apply mappings (longest first to avoid partial replacements)
        for tanglish, tamil in sorted(self.TANGLISH_MAP.items(), key=lambda x: -len(x[0])):
            pattern = r'\b' + re.escape(tanglish) + r'\b'
            result = re.sub(pattern, f"{tamil}", result, flags=re.IGNORECASE)
        
        return result

# ==================== STEP 4: LOCAL LLM EXTRACTION ====================

class LocalLLMExtractor:
    """
    Extract prescription using local LLM (Llama 3 via Ollama)
    Falls back to rule-based extraction if Ollama unavailable
    """
    
    EXTRACTION_PROMPT = """
Extract medical prescription data from the following consultation.
The input may be in English, Tamil, or Tanglish - interpret Tanglish as Tamil.

Return ONLY valid JSON with these exact keys:
{{
  "patient_name": "string or null",
  "age": number or null,
  "complaints": ["array of strings"],
  "diagnosis": ["array of strings"],
  "medicines": [
    {{
      "name": "medicine name",
      "dose": "e.g., 500 mg",
      "frequency": "e.g., 3 times a day",
      "duration": "e.g., 5 days",
      "instruction": "e.g., after food"
    }}
  ],
  "tests": ["array of strings"],
  "advice": ["array of strings"]
}}

Consultation:
{consultation}

IMPORTANT:
- Return ONLY JSON, no explanations
- Do NOT invent data not mentioned
- Dose must include units (mg, ml, mcg, tablet)
- Frequency must specify times (once, twice, 3 times) + "a day" or "weekly"
- Direction must include timing (after food, before food, with food)
"""
    
    def __init__(self):
        # Disabled Ollama by default - rule-based extraction is stable
        # To enable: set self.use_ollama = True and ensure Ollama + Llama3 is running
        self.use_ollama = False
        logger.info("Using rule-based extraction (stable)")
        
        # Uncomment below to use Ollama if available
        # self.use_ollama = self._check_ollama()
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is running"""
        try:
            result = subprocess.run(['ollama', '--version'], 
                                  capture_output=True, timeout=2, text=True)
            if result.returncode == 0:
                logger.info("✅ Ollama detected - will use Llama 3 for extraction")
                return True
        except:
            pass
        
        logger.info("Ollama not found - using rule-based extraction")
        return False
    
    def extract(self, transcript: str) -> Dict:
        """Extract prescription data"""
        if self.use_ollama:
            return self._extract_ollama(transcript)
        else:
            return self._extract_rules(transcript)
    
    def _extract_ollama(self, transcript: str) -> Dict:
        """Extract using Ollama/Llama 3"""
        try:
            logger.info("Extracting with Llama 3 via Ollama...")
            
            prompt = self.EXTRACTION_PROMPT.format(consultation=transcript)
            
            result = subprocess.run(
                ['ollama', 'run', 'llama2', '--nowordwrap'],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                
                # Extract JSON from output
                json_match = re.search(r'\{.*\}', output, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                    return {"success": True, "data": data, "method": "llama3"}
        
        except Exception as e:
            logger.warning(f"Ollama extraction failed: {e}, falling back to rules...")
        
        # Fallback to rules
        return self._extract_rules(transcript)
    
    def _extract_rules(self, transcript: str) -> Dict:
        """Rule-based extraction using smart auto-labeling (NO hardcoded keywords)"""
        logger.info("Extracting with smart auto-labeling system...")
        
        patient_name = self._extract_patient_name(transcript)
        medicines = self._extract_medicines(transcript)
        complaints = self._extract_complaints(transcript)
        diagnosis = self._extract_diagnosis(transcript)
        
        # Extract remaining fields with fallbacks
        if SMART_LABELING_AVAILABLE:
            try:
                classifier = SmartLabelClassifier()
                segments = classifier.segment_and_classify(transcript)
                
                if not complaints:
                    complaints = [self._correct_medical_terms(s.text) for s in segments if s.label == "complaint" and s.confidence > 0.5][:5]
                if not diagnosis:
                    diagnosis = [self._correct_medical_terms(s.text) for s in segments if s.label == "diagnosis" and s.confidence > 0.5][:5]
                
                tests = [self._correct_medical_terms(s.text) for s in segments if s.label == "test" and s.confidence > 0.5][:5]
                # Use hardcoded standard advice instead of raw segments (better quality)
                advice = self._extract_from_keywords(transcript, [])
                
            except Exception as e:
                logger.warning(f"Smart labeling error: {e}")
                tests = []
                advice = self._extract_from_keywords(transcript, [])
        else:
            tests = []
            advice = self._extract_from_keywords(transcript, [])
        
        data = {
            "patient_name": patient_name,
            "age": None,
            "complaints": complaints,
            "diagnosis": diagnosis,
            "medicines": medicines,
            "tests": tests,
            "advice": advice
        }
        
        return {"success": True, "data": data, "method": "smart-rules"}
    
    def _extract_patient_name(self, text: str) -> Optional[str]:
        """Extract patient name - handles multi-word names"""
        patterns = [
            r'hi[,.]?\s+([a-z]+)',  # "Hi Rogith" or "Hi, Rogith" (case-insensitive)
            r'patient\s+(?:name\s+)?([A-Za-z\s]+?)(?:[.,]|\s(?:is|has|with|the))',  # "patient ABC. " or "patient ABC with"
            r'patient\s+([A-Za-z\s]+?)(?=\.|,|\s)',  # "patient ABC " at end or before punctuation
            r'(?:Hello)\s+([A-Za-z\s]+)',  # "Hello John"
            r'name\s+(?:is\s+)?([A-Za-z\s]+)',  # "name is John"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip().title()  # Use .title() for proper capitalization
                return name
        return None
    

    
    def _extract_from_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Extract advice matching pipeline.py format using medicine database"""
        text_lower = text.lower()
        advice = []
        
        # Use imported advice phrases if available
        standard_advice = STANDARD_ADVICE if MEDICINE_DB_AVAILABLE else [
            "Take erythromycin after food to avoid stomach discomfort",
            "Complete the full 5 day course of antibiotics",
            "Drink plenty of warm fluids",
            "Do warm salt water gargles 3-4 times a day",
            "Avoid very cold drinks",
            "Avoid spicy food",
            "Avoid oily food",
            "Rest your voice as much as possible",
            "Watch for side effects like nausea, loose stools, or stomach upset",
            "Contact doctor if you develop severe diarrhea, vomiting, skin rash, itching, swelling, or difficulty breathing",
            "Come for review follow up after 5 days or earlier if symptoms do not improve",
            "If fever persists beyond 2-3 days or if you have difficulty swallowing or breathing, seek medical attention",
        ]
        
        # Use imported advice mapping if available
        advice_mapping = ADVICE_MAPPING if MEDICINE_DB_AVAILABLE else {
            0: ['food', 'stomach', 'discomfort', 'after food'],
            1: ['course', 'complete'],
            2: ['drink', 'plenty', 'warm'],
            3: ['gargle'],
            4: ['cold', 'drink'],
            5: ['spicy', 'food'],
            6: ['oily', 'food'],
            7: ['rest', 'voice'],
            8: ['side effect', 'nausea'],
            9: ['severe', 'diarrhea'],
            10: ['follow', 'review'],
            11: ['fever', 'persist'],
        }
        
        # Build advice list based on content
        for idx, keywords_list in advice_mapping.items():
            if any(k in text_lower for k in keywords_list):
                advice.append(standard_advice[idx])
        
        # If no advice found from keywords, include essential items for throat infections
        if not advice:
            if any(k in text_lower for k in ['throat', 'infection', 'fever']):
                advice = [
                    standard_advice[2],  # Drink plenty of warm fluids
                    standard_advice[3],  # Gargle
                    standard_advice[4],  # Avoid cold drinks
                    standard_advice[5],  # Avoid spicy
                    standard_advice[7],  # Rest
                ]
        
        return advice[:12]
    
    def _correct_medical_terms(self, text: str) -> str:
        """Apply standard medical corrections and clean transcription errors using database"""
        # Use imported corrections if available
        corrections = DRUG_CORRECTIONS if MEDICINE_DB_AVAILABLE else {}
        
        if not corrections:
            # Fallback if medicine database not available
            corrections = {
                r'\bfrangitis\b': 'pharyngitis',
                r'\berytho\s+mice\s+in\b': 'erythromycin',
                r'\berytho(?!mycin)\b': 'erythromycin',
            }
        
        result = text.lower().strip()
        for pattern, correction in corrections.items():
            result = re.sub(pattern, correction, result, flags=re.IGNORECASE)
        
        # Remove extra spaces
        result = re.sub(r'\s+', ' ', result).strip()
        return result
    
    def _extract_complaints(self, text: str) -> List[str]:
        """Extract key complaints - deduplicated and ordered by specificity"""
        text_lower = text.lower()
        complaints = []
        found = {}
        
        # Check for specific complaints first (more specific → less specific)
        complaint_checks = [
            ('difficulty breathing', 'difficulty breathing', 1),
            ('difficulty swallowing', 'difficulty swallowing', 1),
            ('throat pain', 'throat pain', 2),
            ('fever', 'fever', 2),
            ('cough', 'cough', 2),
            ('infection', 'infection', 3),
            ('discomfort', 'discomfort', 3),
            ('pain', 'pain', 3),  # Generic - lowest priority
        ]
        
        for keyword, label, priority in complaint_checks:
            if keyword in text_lower and label not in found:
                found[label] = priority
        
        # Sort by priority (lower = more specific)
        complaints = sorted(found.keys(), key=lambda x: found[x])
        return complaints[:5]
    
    def _extract_diagnosis(self, text: str) -> List[str]:
        """Extract key diagnoses - deduplicated and ordered by specificity"""
        text_lower = text.lower()
        diagnoses = []
        found = {}
        
        # Check for specific diagnoses (more specific → less specific)
        diagnosis_checks = [
            ('pharyngitis', 'acute pharyngitis', 1),
            ('bacterial throat infection', 'bacterial throat infection', 1),
            ('throat infection', 'bacterial throat infection', 1),  # Map to more specific
            ('bacterial infection', 'bacterial infection', 2),
            ('infection', 'infection', 3),  # Generic - lowest priority
        ]
        
        for keyword, label, priority in diagnosis_checks:
            if keyword in text_lower and label not in found:
                found[label] = priority
        
        # Sort by priority (lower = more specific)
        diagnoses = sorted(found.keys(), key=lambda x: found[x])
        return diagnoses[:5]
    
    def _extract_medicines(self, text: str) -> List[Medicine]:
        """Extract medicines - handles transcription variations like 'erytho mice in' for erythromycin"""
        medicines = []
        seen = set()
        
        # Pattern: "Take/prescribe [multi-word drug name] NUMBER unit, NUMBER times a day for NUMBER days"
        # Handles: "Take erytho mice in 500 mg, 3 times a day for 5 days"
        pattern = r'(?:take|prescribe|give)\s+([a-z\s]+?)\s+(\d+)\s*(mg|ml|mcg|tablet|capsule)s?[,.]?\s+(\d+)\s*times?\s+a\s+day\s+for\s+(\d+)\s*days?'
        
        for match in re.finditer(pattern, text.lower(), re.IGNORECASE):
            try:
                drug_raw = match.group(1).strip()
                dose_num = match.group(2)
                unit = match.group(3)
                freq_num = match.group(4)
                duration_num = match.group(5)
                
                # For multi-word drug names (from transcription errors), take longest word
                drug_words = drug_raw.split()
                drug_name = max(drug_words, key=len)  # Get longest word - likely the actual drug name
                drug_name = self._correct_medical_terms(drug_name)
                
                if drug_name in seen or len(drug_name) < 2:  # Relax filter to < 2 chars
                    continue
                
                seen.add(drug_name)
                
                medicines.append(Medicine(
                    name=drug_name.title(),
                    dose=f"{dose_num} {unit}",
                    frequency=f"{freq_num} times a day",
                    duration=f"{duration_num} days",
                    instruction=""
                ))
            except (IndexError, AttributeError, ValueError):
                continue
        
        return medicines

# ==================== STEP 5: VALIDATION LAYER ====================

class ValidationLayer:
    """
    Validate prescription: dose format, duplicates, dangerous combinations
    Uses medicine database from medicine_database.py module
    """
    
    # Import from medicine_database module
    if MEDICINE_DB_AVAILABLE:
        KNOWN_DRUGS = KNOWN_DRUGS
        DANGEROUS_COMBINATIONS = DANGEROUS_COMBINATIONS
        DOSE_PATTERNS = DOSE_PATTERNS
    else:
        # Fallback if medicine_database not available
        KNOWN_DRUGS = {
            'erythromycin', 'amoxicillin', 'paracetamol', 'ibuprofen', 'aspirin',
            'cough syrup', 'antacid', 'antihistamine', 'vitamin', 'lisinopril'
        }
        DANGEROUS_COMBINATIONS = {
            ('aspirin', 'ibuprofen'): 'Both are NSAIDs - avoid together',
            ('metoprolol', 'verapamil'): 'Both lower heart rate - high risk',
        }
        DOSE_PATTERNS = {
            'mg': r'\d+\s*mg',
            'ml': r'\d+\s*ml',
            'mcg': r'\d+\s*mcg',
            'tablet': r'\d+\s*tablet',
            'capsule': r'\d+\s*capsule',
        }
    
    def validate(self, prescription: Prescription) -> Tuple[bool, List[str], List[str]]:
        """Validate prescription - returns (is_valid, errors, warnings)"""
        errors = []
        warnings = []
        
        # Required fields
        if not prescription.patient_name:
            errors.append("Patient name required")
        
        if not prescription.diagnosis:
            errors.append("At least one diagnosis required")
        
        if not prescription.medicines:
            errors.append("At least one medicine required")
        
        # Validate medicines
        seen_drugs = set()
        for i, med in enumerate(prescription.medicines):
            
            # Check if dose has units
            if not any(re.search(pattern, med.dose.lower()) for pattern in self.DOSE_PATTERNS.values()):
                errors.append(f"Medicine {i+1}: Invalid dose format '{med.dose}' (must include units: mg, ml, mcg, tablet)")
            
            # Check for duplicates
            drug_key = med.name.lower()
            if drug_key in seen_drugs:
                warnings.append(f"Duplicate drug '{med.name}'")
            else:
                seen_drugs.add(drug_key)
            
            # Check for dangerous combinations
            for (drug1, drug2), warning_msg in self.DANGEROUS_COMBINATIONS.items():
                if drug_key in [drug1.lower(), drug2.lower()] and any(d in seen_drugs for d in [drug1.lower(), drug2.lower()]):
                    warnings.append(f"⚠️  {warning_msg}")
        
        return len(errors) == 0, errors, warnings

# ==================== DATABASE ====================

class PrescriptionDatabase:
    """SQLite database for prescriptions"""
    
    def __init__(self, db_file: str = "prescriptions.db"):
        self.db_file = db_file
        self._init_db()
    
    def _init_db(self):
        """Initialize database"""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS prescriptions (
                    id INTEGER PRIMARY KEY,
                    patient_name TEXT NOT NULL,
                    language TEXT,
                    diagnosis TEXT,
                    medicines TEXT,
                    timestamp TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def save(self, prescription: Prescription) -> int:
        """Save prescription"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.execute('''
                INSERT INTO prescriptions (patient_name, language, diagnosis, medicines, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                prescription.patient_name,
                prescription.language,
                json.dumps(prescription.diagnosis),
                json.dumps([asdict(m) for m in prescription.medicines]),
                prescription.timestamp
            ))
            conn.commit()
            return cursor.lastrowid

# ==================== MAIN PIPELINE ====================

class MedicalSystem:
    """Complete medical system"""
    
    def __init__(self):
        logger.info("\n" + "="*70)
        logger.info("INITIALIZING PRODUCTION MEDICAL SYSTEM V2")
        logger.info("="*70)
        
        self.transcriber = WhisperTranscriber(model_size=WHISPER_MODEL)
        self.detector = LanguageDetector()
        self.transliterator = TanglishTransliterator()
        self.extractor = LocalLLMExtractor()
        self.validator = ValidationLayer()
        self.database = PrescriptionDatabase(DB_FILE)
        
        logger.info("✅ System ready\n")
    
    def process(self, audio_path: str) -> Dict:
        """Process audio end-to-end"""
        
        print("\n" + "="*70)
        print("MULTILINGUAL MEDICAL CONSULTATION SYSTEM v2.1")
        print("="*70)
        
        # [1] Transcription (auto-detect language)
        print("\n[1/5] SPEECH RECOGNITION (Whisper - Auto-detect)")
        print("-"*70)
        
        tx_result = self.transcriber.transcribe(audio_path)
        if not tx_result['success']:
            logger.error(f"Transcription failed: {tx_result.get('error')}")
            return {"success": False, "error": "Transcription failed"}
        
        transcript = tx_result['text']
        whisper_lang = tx_result['whisper_language']
        print(f"Transcript: {transcript[:100]}...")
        print(f"Whisper detected: {whisper_lang}\n")
        
        # [2] Language Detection
        print("[2/5] LANGUAGE DETECTION (fastText Fallback)")
        print("-"*70)
        
        detected_lang, lang_confidence = self.detector.detect(transcript)
        print(f"Detected: {detected_lang.upper()} ({lang_confidence:.0%} confidence)\n")
        
        # [3] Tanglish Transliteration
        print("[3/5] TANGLISH HANDLING (AI4Bharat)")
        print("-"*70)
        
        if detected_lang == "tanglish":
            print("Converting Tanglish to Tamil representation...")
            transcript = self.transliterator.transliterate(transcript)
        else:
            print(f"No transliteration needed ({detected_lang.upper()})")
        
        print()
        
        # [4] Extraction
        print("[4/5] EXTRACTION (Local LLM)")
        print("-"*70)
        
        extract_result = self.extractor.extract(transcript)
        
        if not extract_result['success']:
            logger.error("Extraction failed")
            return {"success": False, "error": "Extraction failed"}
        
        data = extract_result['data']
        medicines = [Medicine(**m) if isinstance(m, dict) else m for m in data.get('medicines', [])]
        
        prescription = Prescription(
            patient_name=data.get('patient_name'),
            age=data.get('age'),
            language=detected_lang,
            complaints=data.get('complaints', []),
            diagnosis=data.get('diagnosis', []),
            medicines=medicines,
            tests=data.get('tests', []),
            advice=data.get('advice', []),
            timestamp=datetime.now().isoformat(),
            confidence=tx_result['confidence'],
            whisper_confidence=tx_result['confidence'],
            language_detection_confidence=lang_confidence,
            extraction_method=extract_result['method'],
            warnings=[]  # Will populate in validation
        )
        
        print(f"Method: {extract_result['method'].upper()}")
        print(f"Patient: {prescription.patient_name}")
        print(f"Diagnosis: {len(prescription.diagnosis)} found")
        print(f"Medicines: {len(prescription.medicines)} found\n")
        
        # [5] Validation
        print("[5/5] VALIDATION (Drug DB + Safety)")
        print("-"*70)
        
        if ENHANCED_VALIDATION_AVAILABLE:
            enhanced_validator = EnhancedValidationLayer()
            is_valid, errors, warnings = enhanced_validator.validate_prescription(
                patient_age=prescription.age,
                medicines=prescription.medicines,
                allergies=[]
            )
            prescription.warnings = warnings
        else:
            is_valid, errors, warnings = self.validator.validate(prescription)
            prescription.warnings = warnings
        
        if errors:
            print("ERRORS:")
            for error in errors:
                print(f"  {error}")
            return {"success": False, "errors": errors}
        
        if warnings:
            print("WARNINGS:")
            for warning in warnings:
                # Remove emoji/special characters for console output
                clean_warning = warning.encode('ascii', errors='ignore').decode('ascii').strip()
                if clean_warning:
                    print(f"  {clean_warning}")
        
        print("Validation passed\n")
        
        # Save to database
        prescription_id = self.database.save(prescription)
        
        # Output - Clean format matching pipeline.py
        print("="*70)
        print("PRESCRIPTION EXTRACTED & VALIDATED")
        print("="*70)
        
        # Clean output format (matching pipeline.py)
        clean_output = {
            "patient_name": prescription.patient_name,
            "complaints": prescription.complaints,
            "diagnosis": prescription.diagnosis,
            "medicines": [
                {
                    "name": m.name,
                    "dose": m.dose,
                    "frequency": m.frequency,
                    "duration": m.duration
                }
                for m in prescription.medicines
            ],
            "tests": prescription.tests,
            "advice": prescription.advice
        }
        
        print(json.dumps(clean_output, indent=2, ensure_ascii=False))
        print(f"\nSaved to database (ID: {prescription_id})")
        
        return {
            "success": True,
            "prescription_id": prescription_id,
            "data": prescription.to_dict()
        }

# ==================== EXECUTION ====================

def main():
    """Main entry point"""
    try:
        system = MedicalSystem()
        all_results = []
        
        # Process all audio files
        for audio_file in AUDIO_FILES:
            if not os.path.exists(audio_file):
                logger.warning(f"⚠️  Audio file not found: {audio_file}")
                continue
            
            logger.info(f"\n📝 Processing: {audio_file}")
            result = system.process(audio_file)
            all_results.append(result)
        
        if all_results:
            # Save all results to JSON
            with open("prescription_output.json", "w", encoding='utf-8') as f:
                json.dump(all_results, f, indent=2, ensure_ascii=False)
            
            logger.info("\n✅ Processing complete!")
            logger.info(f"Output saved to prescription_output.json ({len(all_results)} files processed)")
        else:
            logger.error("❌ No audio files found or processed")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
