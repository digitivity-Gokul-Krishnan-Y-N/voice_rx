"""
Medical System V2: Production-grade multilingual prescription extraction.
Advanced extraction with improved medicine/diagnosis detection and validation.
"""

import os
import sys
import json
import logging
import sqlite3
import numpy as np
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field

# Load environment
from dotenv import load_dotenv

# Load .env from config directory (works when run from root or src)
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', '.env')
if not os.path.exists(env_path):
    env_path = os.path.join(os.getcwd(), 'config', '.env')
load_dotenv(env_path)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('medical_system_v2.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Import modular components
from transcription import WhisperTranscriber, TranscriptionResult, TranscriptCleaner
from routing import AudioAnalyzer, RouteSelector
from extraction import GroqLLMExtractor, EnsembleExtractor, Medicine
from validation import ValidationLayer, Prescription
from metrics import MetricsCollector, MetricsDashboard, ExtractionMetrics
from language_detection import LanguageDetector
from thanglish_normalizer import ThanglishNormalizer
from normalization import TranscriptNormalizer
import medicine_database

# Configuration
AUDIO_FILES = ["data\WhatsApp Audio 2026-02-20 at 12.36.29 PM.mp4"]  # Example audio file for testing
DB_FILE = "data/prescriptions.db"
# Local Whisper (medium) for transcription + Groq for LLM extraction
WHISPER_MODEL = "medium"
TRANSCRIBER_SOURCE = "local"  # Using local Whisper for cost-effective transcription

# Use centralized Medicine Database
KNOWN_DRUGS = medicine_database.KNOWN_DRUGS
DANGEROUS_COMBINATIONS = medicine_database.DANGEROUS_COMBINATIONS
STANDARD_ADVICE = medicine_database.STANDARD_ADVICE

# ==================== ADVANCED EXTRACTION ====================

class AdvancedExtractor:
    """Advanced extraction with improved medicine/diagnosis detection"""

    def __init__(self):
        self.extractor = GroqLLMExtractor()
        self.ensemble = EnsembleExtractor(self.extractor)

    def extract_advanced(self, transcript: str, use_ensemble: bool = False) -> Dict:
        """Extract with advanced pattern matching"""
        logger.info(f"Running advanced extraction on {len(transcript)} chars...")
        logger.info(f"Transcript begins: {transcript[:150]}...")
        
        # Try primary extraction
        if use_ensemble:
            result = self.ensemble.extract_ensemble(transcript)
        else:
            result = self.extractor.extract(transcript, use_groq=True)
        
        if not result.get('success'):
            logger.info("Primary extraction failed, using rules...")
            result = self._extract_rules_advanced(transcript)
        
        # Log FULL transcript for debugging (in DEBUG level or shorter first 2000 chars)
        logger.debug(f"Full transcript for extraction: {transcript}")
        
        # Post-process: improve extracted data
        data = result.get('data', {})
        logger.info(f"Pre-improvement: medicines={len(data.get('medicines', []))}, diagnosis={len(data.get('diagnosis', []))}")
        
        data['medicines'] = self._improve_medicines(data.get('medicines', []), transcript)
        data['diagnosis'] = self._improve_diagnosis(data.get('diagnosis', []), transcript)
        data['advice'] = self._extract_advice(transcript)
        
        logger.info(f"Post-improvement: medicines={len(data.get('medicines', []))}, diagnosis={len(data.get('diagnosis', []))}")
        
        return {"success": True, "data": data, "method": result.get('method', 'rules')}

    def _extract_rules_advanced(self, transcript: str) -> Dict:
        """Advanced rule-based extraction"""
        logger.info("Extracting with advanced rules...")
        
        patient_name = self._extract_patient_name(transcript)
        medicines = self._extract_medicines_advanced(transcript)
        complaints = self._extract_complaints(transcript)
        diagnosis = self._extract_diagnosis_advanced(transcript)
        advice = self._extract_advice(transcript)
        
        return {
            "success": True,
            "data": {
                "patient_name": patient_name,
                "age": None,
                "complaints": complaints,
                "diagnosis": diagnosis,
                "medicines": medicines,
                "tests": [],
                "advice": advice
            },
            "method": "advanced-rules"
        }

    def _extract_patient_name(self, text: str) -> Optional[str]:
        """Extract patient name from text"""
        # Try to find name in common patterns
        patterns = [
            r'patient\s+(?:named?|is)?\s+([A-Za-z]+)',
            r'(?:hi|hello|hey|like|ok)\s+([A-Z][a-z]+)',  # Greeting/Filler + Name
            r'(?:hi|hello|hey|like|ok)\s+([a-z]+)',        # Greeting/Filler + Name (lowercase)
            r',\s*([A-Z][a-z]+)\s+you\s+have',             # e.g., "Rohit, you have"
            r'\b([A-Z][a-z]+)\s*,\s*([A-Z][a-z]+)\b',      # "Name, Name" pattern
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1)
                # Filter out common filler words and small words
                if len(name) > 1 and name.lower() not in ['you', 'the', 'this', 'that', 'with', 'have', 'your']:
                    return name.capitalize()
        
        # Fallback: find first capitalized word that's not a common word
        words = text.split()
        common_words = {'I', 'It', 'The', 'This', 'That', 'OK', 'Is'}
        for word in words[:20]:
            clean_word = re.sub(r'[^a-zA-Z]', '', word)  # Remove punctuation
            if clean_word and clean_word[0].isupper() and clean_word not in common_words and len(clean_word) > 2:
                return clean_word
        
        return None

    def _extract_medicines_advanced(self, text: str) -> List[Dict]:
        """Extract medicines - handles transcription variations"""
        medicines = []
        seen = set()
        text_lower = text.lower()
        
        # Correct medical term errors first
        corrected_text = self._correct_medical_terms(text_lower)
        
        # Multiple patterns to catch various formats
        patterns = [
            # "prescribe erythromycin 500 mg 3 times a day for 5 days"
            r'(?:prescribe|take|give)\s+(?:a\s+)?(?:tablet\s+of\s+)?([a-z]+(?:\s+[a-z]+)?)\s+(\d+(?:\.\d+)?)\s*(?:mg|ml|mcg|gm|gram|iu|tablet|capsule|drop|unit|mc|mcd|cd)s?\s+(\d+)\s*(?:times?\s+)?(?:a\s+)?day\s+for\s+(\d+)\s*days?',
            # "Medicine, erythromycin, 500 mg daily 3 times for 5 days"
            r'(?:medicine|medicines|drug)[,:]?\s*([a-z]+(?:\s+[a-z]+)?)\s*,?\s+(\d+(?:\.\d+)?)\s*(?:mg|ml|mcg|gm|gram|iu|tablet|capsule|drop|unit|mc|mcd|cd)s?\s+(?:daily\s+)?(\d+)\s*(?:times?)\s+for\s+(\d+)\s*days?',
            # "erythromycin 500 mg three times daily" or similar
            r'(?:^|[,;])\s*([a-z]+(?:\s+[a-z]+)?)\s*,?\s+(\d+(?:\.\d+)?)\s*(?:mg|ml|mcg|gm|gram|iu|tablet|capsule|drop|unit|mc|mcd|cd)s?\s+(?:\d+|three|two|four)\s*(?:times?|x)\s+(?:daily|a\s+day)',
            # Simpler pattern: "erythromycin 500 mg" standalone (extract what we can)
            r'(?:prescription|medicine|take)(?:d)?[,:]?\s*([a-z]+(?:\s+[a-z]+)?)\s+(\d+(?:\.\d+)?)\s*(?:mg|ml|mcg|gm|gram|iu|drop|unit)',
            # Very simple: "Drug X every Y hours" or "Drug X take at night"
            r'([a-z]+(?:\s+[a-z]+)?)\s+(?:(\d+(?:\.\d+)?)\s*(?:mg|ml|mcg|gm|gram|iu|drop|unit))?,?\s+(?:every|at|one\s+)?(?:(\d+)\s*(?:hours?|times?\s+daily|times?\s+a\s+day))?',
            # Sprays/Lozenges: "Benzydamine throat spray use 3-4 times daily"
            r'([a-z]+(?:\s+[a-z]+)?)\s+(?:throat\s+)?(?:spray|lozenge|tablet|syrup|supplement)\s+(?:use|take|dissolve)?\s*(\d+(?:-\d+)?)\s*times?\s+(?:daily|a\s+day)',
            # Simple once daily: "Drug X once a day/daily"
            r'([a-z]+(?:\s+[a-z]+)?)\s+(?:take\s+)?(?:once\s+a\s+day|once\s+daily|daily)',
        ]
        
        for pattern_idx, pattern in enumerate(patterns):
            for match in re.finditer(pattern, corrected_text, re.IGNORECASE):
                try:
                    groups = match.groups()
                    
                    if len(groups) < 1:
                        continue
                    
                    drug_raw = groups[0].strip()
                    
                    # Determine unit from the matched text
                    unit = 'mg'
                    dose_num = ''
                    match_text = match.group(0).lower()
                    if 'ml' in match_text:
                        unit = 'ml'
                    elif 'mcg' in match_text:
                        unit = 'mcg'
                    elif 'tablet' in match_text:
                        unit = 'tablet'
                    elif 'capsule' in match_text:
                        unit = 'capsule'
                    
                    # Extract dose number if available
                    if len(groups) >= 2 and groups[1]:
                        dose_num = groups[1]
                    else:
                        # Try to find dose in the match text
                        dose_match = re.search(r'(\d+)\s*(?:mg|ml|mcg)', match_text)
                        if dose_match:
                            dose_num = dose_match.group(1)
                    
                    # Skip if it's a verb/non-drug word
                    if drug_raw in ['prescribe', 'take', 'give', 'tablet', 'medicine', 'drug', 'medicines', 'prescription', 'every', 'one', 'at']:
                        continue
                    
                    # Get just the first word (primary drug name)
                    drug_name = drug_raw.split()[0] if drug_raw.split() else ""
                    drug_name = self._correct_medical_terms(drug_name.strip())
                    
                    if drug_name in seen or len(drug_name) < 2:
                        continue
                    
                    # Extract frequency from the match string (default to "1 times a day" if not found)
                    if len(groups) >= 3 and groups[2]:
                        freq_num = groups[2]
                    else:
                        freq_match = re.search(r'(\d+)\s*(?:times?|x|hours?)', match.group(0), re.IGNORECASE)
                        freq_num = freq_match.group(1) if freq_match else "1"
                    
                    # Extract duration (default to "5 days" if not found)
                    if len(groups) >= 4 and groups[3]:
                        duration_num = groups[3]
                    else:
                        dur_match = re.search(r'for\s+(\d+)\s*days?', match.group(0), re.IGNORECASE)
                        duration_num = dur_match.group(1) if dur_match else "5"
                    
                    seen.add(drug_name)
                    
                    # Build dose string - optional if not found
                    dose_str = f"{dose_num} {unit}" if dose_num else unit
                    
                    medicines.append({
                        "name": drug_name.lower(),
                        "dose": dose_str,
                        "frequency": f"{freq_num} times a day",
                        "duration": f"{duration_num} days",
                        "instruction": "",
                        "route": "oral",
                        "side_effects": []
                    })
                    
                except (IndexError, AttributeError, ValueError):
                    continue
        
        return medicines

    def _extract_complaints(self, text: str) -> List[str]:
        """Extract key complaints - deduplicated"""
        text_lower = text.lower()
        complaints = []
        found = {}
        
        complaint_checks = [
            ('difficulty breathing', 'difficulty breathing', 1),
            ('difficulty swallowing', 'difficulty swallowing', 1),
            ('throat pain', 'throat pain', 2),
            ('fever', 'fever', 2),
            ('cough', 'cough', 2),
            ('infection', 'infection', 3),
            ('discomfort', 'discomfort', 3),
            ('pain', 'pain', 3),
        ]
        
        for keyword, label, priority in complaint_checks:
            if keyword in text_lower and label not in found:
                found[label] = priority
        
        complaints = sorted(found.keys(), key=lambda x: found[x])
        return complaints[:5]

    def _extract_diagnosis_advanced(self, text: str) -> List[str]:
        """Extract diagnoses with transcription error handling"""
        text_lower = text.lower()
        # Correct medical terms first to catch transcription errors
        corrected_text = self._correct_medical_terms(text_lower)
        diagnoses = []
        found = {}
        
        # Handle common transcription errors and variations
        diagnosis_checks = [
            ('pharyngitis', 'acute pharyngitis', 1),
            ('sinusitis', 'acute sinusitis', 1),
            ('sinus', 'sinusitis', 2),
            ('bronchitis', 'acute bronchitis', 1),
            ('bacterial\s+throat', 'bacterial throat infection', 1),
            ('throat\s+infection', 'throat infection', 1),
            ('bacterial\s+infection', 'bacterial infection', 2),
            ('viral\s+infection', 'viral infection', 2),
            ('infection', 'infection', 3),
            ('pneumonia', 'pneumonia', 1),
            ('asthma', 'asthma', 2),
            ('diabetes', 'diabetes', 2),
            ('hypertension', 'hypertension', 2),
            ('fever', 'fever', 3),
        ]
        
        for keyword, label, priority in diagnosis_checks:
            if re.search(keyword, corrected_text, re.IGNORECASE) and label not in found:
                found[label] = priority
        
        diagnoses = sorted(found.keys(), key=lambda x: found[x])
        return diagnoses[:5]

    def _extract_advice(self, text: str) -> List[str]:
        """Extract or generate advice"""
        text_lower = text.lower()
        advice = []
        
        advice_keywords = {
            0: ['food', 'stomach', 'discomfort', 'after food', 'apram'],
            1: ['course', 'complete'],
            2: ['drink', 'plenty', 'warm', 'fluids', 'kudichuko', 'kurichiko'],
            3: ['gargle', 'salt water'],
            4: ['cold', 'drink', 'cold drinks'],
            5: ['spicy', 'food', 'spicy food'],
            6: ['oily', 'food', 'oily food'],
            7: ['rest', 'voice', 'rest your'],
            8: ['side effect', 'nausea', 'mild side'],
            9: ['severe', 'diarrhea'],
            10: ['follow', 'review', 'vaa'],
            11: ['fever', 'persist', 'fever for'],
        }
        
        for idx, keywords_list in advice_keywords.items():
            if any(k in text_lower for k in keywords_list):
                advice.append(STANDARD_ADVICE[idx])
        
        # If no advice found, generate basics
        if not advice and any(k in text_lower for k in ['throat', 'infection', 'fever']):
            advice = [
                STANDARD_ADVICE[2],  # Drink warm fluids
                STANDARD_ADVICE[3],  # Gargle
                STANDARD_ADVICE[4],  # Avoid cold
                STANDARD_ADVICE[5],  # Avoid spicy
            ]
        
        return advice[:12]

    def _improve_medicines(self, medicines: List, text: str) -> List[Dict]:
        """Post-process medicines list - extract if empty"""
        # If we already have medicines, return them
        if isinstance(medicines, list) and len(medicines) > 0:
            if isinstance(medicines[0], dict):
                return medicines
        
        # Otherwise, extract from text with improved method
        extracted = self._extract_medicines_advanced(text)
        return extracted if extracted else medicines

    def _improve_diagnosis(self, diagnoses: List[str], text: str) -> List[str]:
        """Post-process diagnosis list - extract if empty"""
        if diagnoses and len(diagnoses) > 0:
            return diagnoses
        return self._extract_diagnosis_advanced(text)

    def _correct_medical_terms(self, text: str) -> str:
        """Correct common transcription errors"""
        result = text.lower().strip()
        
        # Apply central corrections from database
        if hasattr(medicine_database, 'DRUG_CORRECTIONS'):
            for pattern, correction in medicine_database.DRUG_CORRECTIONS.items():
                result = re.sub(pattern, correction, result, flags=re.IGNORECASE)
        
        # Additional system-specific/filler corrections
        corrections = {
            r'\bparagenesis\b': 'pharyngitis',
            r'\bpyrogynous\b': 'pharyngitis',
            r'\bparakinesis\b': 'pharyngitis',
            r'\bthroat\s+infraction\b': 'throat infection',
            r'\bbacterial\s+fracture\b': 'bacterial infection',
            r'\binflection\b': 'infection',
            r'\bback\s+inflection\b': 'bacterial infection',
            r'\bantibiotic\s+risk\b': 'antibiotics',
        }
        
        for pattern, correction in corrections.items():
            result = re.sub(pattern, correction, result, flags=re.IGNORECASE)
        
        return result


# ==================== PRESCRIPTION DATABASE ====================

class PrescriptionDatabase:
    """SQLite database for prescriptions"""

    def __init__(self, db_file: str = "prescriptions.db"):
        self.db_file = db_file
        self._init_db()

    def _init_db(self):
        """Initialize database"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_file) or '.', exist_ok=True)
        
        with sqlite3.connect(self.db_file) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS prescriptions (
                    id INTEGER PRIMARY KEY,
                    patient_name TEXT,
                    language TEXT,
                    diagnosis TEXT,
                    medicines TEXT,
                    extraction_method TEXT,
                    routing_decision TEXT,
                    confidence REAL,
                    timestamp TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def save(self, prescription: Prescription, routing_decision: str = "unknown") -> int:
        """Save prescription to database"""
        # Fallback for missing patient name to satisfy DB constraints if still NOT NULL
        patient_name = prescription.patient_name or "Unknown Patient"
        
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.execute('''
                INSERT INTO prescriptions 
                (patient_name, language, diagnosis, medicines, extraction_method, 
                 routing_decision, confidence, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                patient_name,
                prescription.language,
                json.dumps(prescription.diagnosis),
                json.dumps(prescription.medicines),
                prescription.extraction_method,
                routing_decision,
                prescription.confidence,
                prescription.timestamp or datetime.now().isoformat()
            ))
            conn.commit()
            return cursor.lastrowid


# ==================== MAIN MEDICAL SYSTEM ====================

class MedicalSystem:
    """Production medical system with advanced extraction"""

    def __init__(self):
        logger.info("\n" + "=" * 80)
        logger.info("INITIALIZING PRODUCTION MEDICAL SYSTEM V2 (Advanced Extraction)")
        logger.info("=" * 80)

        # Core components
        self.transcriber = WhisperTranscriber(model_size=WHISPER_MODEL)
        self.language_detector = LanguageDetector()
        self.thanglish_normalizer = ThanglishNormalizer()
        self.transcript_normalizer = TranscriptNormalizer()
        self.advanced_extractor = AdvancedExtractor()

        # Intelligent routing
        self.analyzer = AudioAnalyzer()
        self.router = RouteSelector()

        # Validation
        self.validator = ValidationLayer()
        self.database = PrescriptionDatabase(DB_FILE)

        # Metrics collection
        self.metrics_collector = MetricsCollector()

        logger.info("[OK] System ready with advanced extraction\n")

    def process(self, audio_path: str, language: Optional[str] = None) -> Dict:
        """
        Process audio file end-to-end with clean architecture.

        Args:
            audio_path: Path to audio file
            language:   Optional language override ('en', 'ta', 'tanglish').
                        If None, auto-detected from audio (probe pass).
        """
        start_time = datetime.now()

        print("\n" + "=" * 80)
        print("MEDICAL CONSULTATION EXTRACTION - GROQ-FIRST SYSTEM")
        print("=" * 80)

        # [1] Transcription
        lang_label = f"forced='{language}'" if language else "auto-detect"
        print(f"\n[1/7] SPEECH RECOGNITION (Whisper multilingual, {lang_label})")
        print("-" * 80)

        tx_result = self.transcriber.transcribe(audio_path, language=language)
        if not tx_result.success:
            logger.error(f"Transcription failed: {tx_result.error}")
            return {"success": False, "error": "Transcription failed"}

        transcript = tx_result.text
        tier_label = {1: "base (multilingual, auto-detect)", 2: "base (multilingual, with hint)", 3: "medium (multilingual, escalated)"}.get(
            tx_result.transcription_tier, str(tx_result.transcription_tier)
        )
        print(f"Model: Whisper {tier_label}")
        print(f"Mode: transcribe (native multilingual ASR)")
        print(f"Raw length: {len(transcript)} chars")
        try:
            print(f"Raw transcript: {transcript[:100]}...")
        except UnicodeEncodeError:
            print(f"Raw transcript: [Non-ASCII text]")
        print(f"Confidence: {tx_result.confidence:.0%}")
        audio_detected_lang = tx_result.detected_language or "en"
        print(f"Audio-detected language: {audio_detected_lang.upper()} (Whisper raw: {tx_result.whisper_language})\n")

        # [2] Transcript Cleaning (NEW)
        print("[2/7] TRANSCRIPT CLEANING (ASR distortion fixes)")
        print("-" * 80)
        
        cleaner = TranscriptCleaner()
        cleaned_transcript, was_modified = cleaner.clean(transcript)
        
        print(f"Cleaning applied: {'Yes' if was_modified else 'No'}")
        print(f"Cleaned length: {len(cleaned_transcript)} chars")
        if was_modified and len(cleaned_transcript) < 200:
            print(f"Cleaned transcript: {cleaned_transcript}")
        else:
            print(f"Cleaned (sample): {cleaned_transcript[:100]}...")
        print()

        # Use cleaned transcript for all downstream processing
        transcript = cleaned_transcript

        # [3] Language Detection
        print("[3/7] LANGUAGE DETECTION")
        print("-" * 80)

        # Audio-level language already detected by Whisper probe.
        # Run text-level detector as secondary confirmation.
        # If Whisper already detected Tamil or Thanglish, trust it over text-only fallback.
        text_lang_code, text_lang_metadata = self.language_detector.detect(transcript)

        # Merge: audio detection wins for 'ta' (Tamil Unicode), text detection wins for 'tanglish'
        if audio_detected_lang == "ta":
            lang_code = "ta"
            lang_metadata = {"confidence": 0.95, "reason": "Tamil detected by Whisper (audio-level)"}
        elif audio_detected_lang == "tanglish" or text_lang_code == "tanglish":
            lang_code = "tanglish"
            lang_metadata = {
                "confidence": max(
                    text_lang_metadata.get("confidence", 0.0),
                    0.85 if audio_detected_lang == "tanglish" else 0.0,
                ),
                "reason": f"Thanglish detected (audio={audio_detected_lang}, text={text_lang_code})"
            }
        else:
            lang_code, lang_metadata = text_lang_code, text_lang_metadata

        lang_confidence = lang_metadata.get('confidence', 0.0)
        
        print(f"Audio-level: {audio_detected_lang.upper()}")
        print(f"Text-level:  {text_lang_code.upper()}")
        print(f"Final:       {lang_code.upper()} (confidence: {lang_confidence:.0%})")
        if 'reason' in lang_metadata:
            print(f"Reason: {lang_metadata['reason']}")
        print()

        # [4] Thanglish Normalization (if needed)
        print("[4/7] THANGLISH NORMALIZATION")
        print("-" * 80)

        if lang_code == "tanglish":
            transcript, was_thanglish_normalized = self.thanglish_normalizer.normalize(transcript)
            print(f"Thanglish normalized: {was_thanglish_normalized}")
            print(f"Normalized (sample): {transcript[:100]}...")
        else:
            print(f"No Thanglish normalization needed ({lang_code.upper()})")
            was_thanglish_normalized = False
        print()

        # [5] Transcript Normalization (ASR fixes, dosage/frequency standardization)
        print("[5/7] TRANSCRIPT NORMALIZATION (ASR fixes, dosage standardization)")
        print("-" * 80)

        transcript, norm_metadata = self.transcript_normalizer.normalize(transcript)
        norm_steps = norm_metadata.get('steps', [])
        
        print(f"Normalization steps applied: {len(norm_steps)}")
        if norm_steps and len(norm_steps) <= 5:
            for step in norm_steps:
                print(f"  - {step}")
        elif norm_steps:
            print(f"  - {norm_steps[0]}")
            print(f"  - ... ({len(norm_steps)-2} more steps)")
            print(f"  - {norm_steps[-1]}")
        
        print(f"Normalized (sample): {transcript[:100]}...")
        print()

        # [6] Intelligent Routing & Groq-First Extraction
        print("[6/7] GROQ-FIRST ROUTING & EXTRACTION")
        print("-" * 80)

        analysis = self.analyzer.analyze(
            transcript=transcript,
            whisper_confidence=tx_result.confidence,
            language=lang_code,
            language_confidence=lang_confidence
        )

        route, routing_config = self.router.select_route(analysis)

        # 🔥 SAFETY: If audio is corrupted (transcription produced almost nothing), skip extraction
        if route == 'corrupted_audio':
            print(f"Route: {route.upper()}")
            print("Status: Audio quality too poor - cannot extract prescription")
            print("\n[7/7] VALIDATION (SKIPPED)")
            print("-" * 80)
            print("Status: Audio appears corrupted or missing")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Return empty prescription as dict (JSON serializable)
            output = {
                "success": False,
                "error": "Audio appears corrupted or missing",
                "patient_name": None,
                "complaints": [],
                "diagnosis": [],
                "medicines": [],
                "tests": [],
                "advice": ["Please provide a clear audio recording"],
                "language": lang_code,
                "confidence": 0.0,
                "extraction_method": "corrupted_audio",
                "timestamp": datetime.now().isoformat(),
                "processing_time_sec": processing_time,
                "route": route
            }
            
            print(json.dumps({
                "patient_name": output["patient_name"],
                "complaints": output["complaints"],
                "diagnosis": output["diagnosis"],
                "medicines": output["medicines"],
                "tests": output["tests"],
                "advice": output["advice"]
            }, indent=2, ensure_ascii=False))
            
            return output

        # Execute extraction based on route (Groq-first)
        use_ensemble = (route == 'ensemble')
        print(f"Route: {route.upper()}")
        print(f"Extraction method: {'Groq (primary)' if route == 'groq_only' else 'Groq + Rules (voting)' if route == 'ensemble' else 'Rules-only (fallback)'}")
        
        logger.info(f"[OPTIMIZATION] Ensemble disabled by default for speed. Using Groq-only mode.")
        use_ensemble = False  # 🔥 DISABLE ENSEMBLE BY DEFAULT - runs both methods (SLOW)
        
        # Debug: log full transcript for extraction
        logger.info(f"Full cleaned transcript for extraction ({len(transcript)} chars): {transcript[:1000]}...")
        
        extract_result = self.advanced_extractor.extract_advanced(
            transcript=transcript,
            use_ensemble=use_ensemble
        )

        if not extract_result['success']:
            logger.error("Advanced extraction failed")
            return {"success": False, "error": "Extraction failed"}

        data = extract_result['data']
        medicines = [Medicine(**m) if isinstance(m, dict) else m for m in data.get('medicines', [])]

        prescription = Prescription(
            patient_name=data.get('patient_name'),
            age=data.get('age'),
            language=lang_code,
            complaints=data.get('complaints', []),
            diagnosis=data.get('diagnosis', []),
            medicines=[vars(m) for m in medicines],
            tests=data.get('tests', []),
            advice=data.get('advice', []),
            confidence=analysis.get('overall_quality', tx_result.confidence),
            extraction_method=f"{route}:{extract_result['method']}",
            transcription_tier=tx_result.transcription_tier
        )

        print(f"Extraction method: {extract_result['method'].upper()}")
        print(f"Patient name: {prescription.patient_name}")
        print(f"Diagnosis: {len(prescription.diagnosis)} found")
        print(f"Medicines: {len(prescription.medicines)} found\n")

        # [7] Validation
        print("[7/7] VALIDATION")
        print("-" * 80)

        is_valid, errors, warnings = self.validator.validate(prescription)

        if errors:
            print("❌ ERRORS:")
            for error in errors:
                print(f"  {error}")

        if warnings:
            print("⚠️  WARNINGS:")
            for warning in warnings:
                clean = warning.encode('ascii', errors='ignore').decode('ascii').strip()
                if clean:
                    print(f"  {clean}")

        if is_valid:
            print("✅ Validation passed\n")
        else:
            print("⚠️  Validation completed with errors - but returning data anyway\n")

        # Save to database (even if validation fails, save the data)
        prescription_id = self.database.save(prescription, routing_decision=route)

        # Output JSON
        print("=" * 80)
        print("PRESCRIPTION EXTRACTED & VALIDATED")
        print("=" * 80)

        output = {
            "patient_name": prescription.patient_name,
            "complaints": prescription.complaints,
            "diagnosis": prescription.diagnosis,
            "medicines": prescription.medicines,
            "tests": prescription.tests,
            "advice": prescription.advice
        }

        print(json.dumps(output, indent=2, ensure_ascii=False))
        print(f"\nSaved to database (ID: {prescription_id})")

        # Record metrics
        processing_time = (datetime.now() - start_time).total_seconds()
        metrics = ExtractionMetrics(
            audio_file=audio_path,
            timestamp=datetime.now().isoformat(),
            transcription_tier=tx_result.transcription_tier,
            transcript_length=len(tx_result.text),  # Raw length before cleaning
            cleaned_length=len(transcript),  # Length after cleaning
            transcript_was_modified=was_modified,
            detected_language=lang_code,
            routing_quality_score=analysis['overall_quality'],
            routing_decision=route,
            extraction_method=extract_result['method'],
            medicines_extracted=len(prescription.medicines),
            diagnosis_extracted=len(prescription.diagnosis),
            validation_passed=is_valid,
            validation_errors=errors,
            validation_warnings=warnings,
            confidence=prescription.confidence,
            processing_time_sec=processing_time
        )
        self.metrics_collector.record(metrics)

        return {
            "success": True,
            "patient_name": prescription.patient_name,
            "complaints": prescription.complaints,
            "diagnosis": prescription.diagnosis,
            "medicines": prescription.medicines,
            "tests": prescription.tests,
            "advice": prescription.advice,
            "language": prescription.language,
            "confidence": prescription.confidence,
            "extraction_method": extract_result.get('method'),
            "processing_time_sec": processing_time,
            "route": route
        }


# ==================== MAIN ENTRY POINT ====================

def main():
    """Main entry point"""
    try:
        system = MedicalSystem()
        all_results = []

        # Process audio files
        for audio_file in AUDIO_FILES:
            if not os.path.exists(audio_file):
                logger.warning(f"[WARNING] Audio file not found: {audio_file}")
                continue

            logger.info(f"\n[PROCESSING] Processing: {audio_file}")
            result = system.process(audio_file)
            all_results.append(result)

        # Save results
        if all_results:
            with open("prescription_output.json", "w", encoding='utf-8') as f:
                json.dump(all_results, f, indent=2, ensure_ascii=False)

            logger.info("\n[OK] Processing complete!")
            logger.info(f"Output saved to prescription_output.json ({len(all_results)} files)")

            # Export metrics (no dashboard display)
            system.metrics_collector.export_json("metrics.json")

        else:
            logger.error("[ERROR] No audio files found")

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
