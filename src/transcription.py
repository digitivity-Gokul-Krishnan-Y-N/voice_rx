"""
Transcription Module: OpenAI Whisper API-based audio transcription.

Supports UNLABELED voice input — automatically detects spoken language:
  - English: Transcribed with medical prompt in English
  - Tamil (Unicode): Transcribed with Tamil language hint, output translated to English
  - Thanglish: Transcribed in multilingual mode with Thanglish-aware prompt

Detection strategy:
  1. Probe pass (short, no language hint) → Whisper reports detected language
  2. Confirm with LanguageDetector on probe text → decide final mode
  3. Full transcription with correct language + prompt

Cleaning:
  After transcription, apply TranscriptCleaner to fix any ASR distortions.
"""

import os
import logging
import re
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI SDK not installed. Install with: pip install openai")

# Load environment
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', '.env')
if not os.path.exists(env_path):
    env_path = os.path.join(os.getcwd(), 'config', '.env')
load_dotenv(env_path)

logger = logging.getLogger(__name__)


@dataclass
class TranscriptionResult:
    """Standard transcription output format."""
    success: bool
    text: str = ""
    whisper_language: str = ""      # Language code Whisper detected
    detected_language: str = ""     # Final resolved language: 'en', 'ta', 'tanglish'
    confidence: float = 0.0
    transcription_tier: int = 1
    cleaned_length: int = 0
    error: Optional[str] = None


# ==================== TRANSCRIPT CLEANING ====================

class TranscriptCleaner:
    """
    Clean medical transcripts by fixing ASR distortions.
    Applied after Whisper transcription but before routing/extraction.
    """

    # Common Whisper ASR errors for English medical text
    ASR_CORRECTIONS = {
        # Phonetic confusions
        r'\binflection\b': 'infection',
        r'\binfraction\b': 'infection',
        r'\binfractions\b': 'infections',
        r'\bback\s+inflection\b': 'bacterial infection',
        r'\bbacterial\s+infraction\b': 'bacterial infection',
        
        # Transcription degradations
        r'\bparagenesis\b': 'pharyngitis',
        r'\bfrangitis\b': 'pharyngitis',
        r'\bfrench\s+dices\b': 'pharyngitis',
        r'\banti(?:biotic\s+)?risk\b': 'antibiotics',
        r'\bacteria(?!l)\b': 'bacterial',
        
        # Drug name distortions
        r'\berytho(?!mycin)\s+mice\s+in\b': 'erythromycin',
        r'\berytho\s+mice\s+in\b': 'erythromycin',
        r'\berythomycin\b': 'erythromycin',
        r'\bamoxycillin\b': 'amoxicillin',
        r'\bamoxylin\b': 'amoxicillin',
        r'\bparacetamole\b': 'paracetamol',
        r'\baccetaminophen\b': 'paracetamol',
        r'\baccetaminife\b': 'acetaminophen',
        r'\basprine\b': 'aspirin',
        r'\biomeprazole\b': 'omeprazole',
        r'\bomeprazole\b': 'omeprazole',
        r'\branitidine\b': 'ranitidine',
        r'\bisoniazid\b': 'isoniazid',
        r'\brifampicin\b': 'rifampicin',
        r'\bmetaphormion\b': 'metformin',
        r'\bglibenclamide\b': 'glibenclamide',
        
        # Frequency/dosage fixes
        r'\bno\s+speech\b': 'no speech',
        r'\bone\s+time\b': 'once',
        r'\btwo\s+times?\b': 'twice',
        r'\bthree\s+times?\b': '3 times',
        r'\bfour\s+times?\b': '4 times',
        r'\bonce\s+a\s+day\b': 'once a day',
        r'\btwice\s+a\s+day\b': 'twice a day',
        r'\bthrice\s+a\s+day\b': '3 times a day',
    }

    # Unit formatting normalization
    UNIT_PATTERNS = {
        r'\b(\d+)mg\b': r'\1 mg',       # 500mg → 500 mg
        r'\b(\d+)ml\b': r'\1 ml',       # 10ml → 10 ml
        r'\b(\d+)mcg\b': r'\1 mcg',     # 100mcg → 100 mcg
        r'\b(\d+)gm\b': r'\1 gm',       # 1gm → 1 gm
        r'\b(\d+)gram\b': r'\1 gm',     # 1gram → 1 gm
        r'\b(\d+)tablet\b': r'\1 tablet',
        r'\b(\d+)capsule\b': r'\1 capsule',
    }

    def clean(self, text: str) -> Tuple[str, bool]:
        """
        Clean transcript.
        
        Returns:
            (cleaned_text, was_modified)
        """
        if not text or not isinstance(text, str):
            return text, False

        original = text
        cleaned = text.lower().strip()

        # Apply ASR corrections
        for pattern, replacement in self.ASR_CORRECTIONS.items():
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)

        # Normalize units
        for pattern, replacement in self.UNIT_PATTERNS.items():
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)

        # Remove duplicate consecutive words
        words = cleaned.split()
        deduped = []
        for word in words:
            if not deduped or word.lower() != deduped[-1].lower():
                deduped.append(word)
        cleaned = ' '.join(deduped)

        # Capitalize first letter
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:]

        was_modified = cleaned.lower() != original.lower()
        return cleaned, was_modified


class WhisperTranscriber:
    """
    OpenAI Whisper API-based transcriber with AUTO LANGUAGE DETECTION.

    Handles UNLABELED voice input — no need to specify language upfront.

    Detection flow:
      1. PROBE PASS  — short Whisper call (no language hint) to detect spoken language
      2. TEXT CONFIRM — LanguageDetector validates probe text for Thanglish markers
      3. FULL PASS   — transcribe with correct language hint + language-specific prompt

    Supported languages:
      - 'en'       → English medical prompt
      - 'ta'       → Tamil + translate-to-English instruction
      - 'tanglish' → Multilingual prompt (Tamil in English letters)
    """

    MEDICAL_KEYWORDS = {
        "mg", "ml", "tablet", "capsule", "dose", "medicine", "drug", "infection",
        "fever", "pain", "antibiotic", "diagnosis", "prescription", "erythromycin",
        "amoxicillin", "paracetamol", "acetaminophen", "ranitidine", "ibuprofen",
        "symptoms", "treatment", "daily", "twice", "thrice", "morning", "night",
        "days", "weeks", "throat", "cough", "cold", "bacterial", "pharyngitis",
        "bronchitis", "pneumonia", "infection", "allergy", "asthma",
        # Tamil/Thanglish medical keywords for quality check
        "marunthu", "vali", "kaichal", "noi", "sapadu",
    }
    MIN_WORDS = 15  # Minimum acceptable words in transcript

    # Language-specific Whisper prompts for better accuracy
    PROMPTS = {
        "en": (
            "Medical consultation in English. Doctor prescribing medicines. "
            "Include drug names, dosages, frequency, and patient advice."
        ),
        "ta": (
            "மருத்துவ ஆலோசனை. மருத்துவர் மருந்துகளை பரிந்துரைக்கிறார். "
            "Translate all content to English medical terminology."
        ),
        "ar": (
            "استشارة طبية. الطبيب يوصي بالأدوية. "
            "Include medicine names, dosages, frequency in medical terminology."
        ),
        "tanglish": (
            "Medical consultation. Patient name, diagnosis, medicines with dosages. "
            "Drug names, frequencies, durations. Tamil-origin words may appear."
        ),
    }

    def __init__(self, model_size: str = "base"):
        """Initialize OpenAI Whisper transcriber."""
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI SDK not available. Install with: pip install openai")

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment. Please configure it in config/.env")

        self.client = OpenAI(api_key=api_key)
        self.cleaner = TranscriptCleaner()

        # Import LanguageDetector for text-level Thanglish confirmation
        try:
            from language_detection import LanguageDetector
            self.lang_detector = LanguageDetector()
        except ImportError:
            self.lang_detector = None
            logger.warning("[WARN] LanguageDetector not available — text-level detection disabled")

        logger.info("[OK] OpenAI Whisper transcriber initialized (auto language detection enabled)")

    # ── Public API ─────────────────────────────────────────────────────────────

    def transcribe(self, audio_path: str, language: Optional[str] = None) -> TranscriptionResult:
        """
        Transcribe audio with automatic language detection.

        Args:
            audio_path: Path to the audio file (.wav, .mp3, .mp4, etc.)
            language:   Optional override. If None, auto-detect from audio.
                        Pass 'en', 'ta', or 'tanglish' to skip detection.

        Returns:
            TranscriptionResult with detected_language field populated.
        """
        try:
            if not os.path.exists(audio_path):
                logger.error(f"Audio file not found: {audio_path}")
                return TranscriptionResult(success=False, error=f"File not found: {audio_path}")

            # ── Step 1: Detect language if not provided ─────────────────────
            if language:
                detected_lang = language
                if language == "ta":
                    whisper_lang = "ta"
                elif language == "ar":
                    whisper_lang = "ar"
                else:
                    whisper_lang = "en"
                logger.info(f"[LANG] Using provided language: {language}")
            else:
                detected_lang, whisper_lang = self._detect_language_from_audio(audio_path)

            # ── Step 2: Full transcription with correct language ────────────
            raw_text = self._transcribe_with_language(audio_path, detected_lang, whisper_lang)
            if raw_text is None:
                return TranscriptionResult(success=False, error="Transcription returned empty text")

            logger.info(f"[WHISPER] Raw transcript ({len(raw_text)} chars): {raw_text[:120]}...")

            # ── Step 3: Clean transcript ────────────────────────────────────
            cleaned_text, was_modified = self.cleaner.clean(raw_text)
            if was_modified:
                logger.debug(f"[CLEAN] Applied corrections: {len(raw_text)} → {len(cleaned_text)} chars")

            # ── Step 4: Quality check ───────────────────────────────────────
            if not self._quality_ok(cleaned_text):
                logger.warning("[QUALITY] Transcript is sparse but proceeding anyway")

            return self._build_result(cleaned_text, detected_lang, whisper_lang)

        except Exception as e:
            logger.error(f"[ERROR] OpenAI transcription failed: {e}")
            return TranscriptionResult(success=False, error=str(e))

    # ── Language detection ─────────────────────────────────────────────────────

    def _detect_language_from_audio(self, audio_path: str) -> tuple:
        """
        Detect spoken language from unlabeled audio using a two-step approach:
          1. Probe Whisper with no language hint — get Whisper's best guess
          2. Run LanguageDetector on probe text — confirm Thanglish vs English

        Returns:
            (detected_lang, whisper_lang)
            detected_lang: 'en', 'ta', or 'tanglish'
            whisper_lang:  Whisper API language code ('en', 'ta', or None for auto)
        """
        logger.info("[DETECT] Probing audio for language detection (no language hint)...")

        try:
            with open(audio_path, "rb") as audio_file:
                probe_response = self.client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-1",
                    # No language= parameter → Whisper auto-detects
                    response_format="verbose_json",  # Gives us language + segments
                )

            whisper_detected = getattr(probe_response, "language", "en") or "en"
            probe_text = getattr(probe_response, "text", "").strip()

            logger.info(f"[DETECT] Whisper detected language: '{whisper_detected}'")
            logger.info(f"[DETECT] Probe text sample: {probe_text[:100]}")

            # ── Map Whisper language to our categories ────────────────────
            if whisper_detected == "tamil" or whisper_detected == "ta":
                # Could be pure Tamil OR Thanglish — check text for Thanglish markers
                if self.lang_detector and probe_text:
                    text_lang, meta = self.lang_detector.detect(probe_text)
                    if text_lang == "tanglish":
                        logger.info(f"[DETECT] Tamil audio but text has Thanglish markers → 'tanglish' mode")
                        return "tanglish", "en"  # Thanglish: transcribe as English
                    else:
                        logger.info(f"[DETECT] Pure Tamil detected → 'ta' mode")
                        return "ta", "ta"  # Pure Tamil
                else:
                    return "ta", "ta"

            elif whisper_detected in ("english", "en"):
                # English — but COULD be Thanglish (Tamil-origin words in English script).
                # Require a HIGH threshold to override Whisper's 'english' judgement.
                # Low counts (≤5) are likely just English medical terms being flagged,
                # not genuine Tamil-in-English-script (Thanglish).
                THANGLISH_OVERRIDE_THRESHOLD = 6  # require strong evidence to override
                if self.lang_detector and probe_text:
                    text_lang, meta = self.lang_detector.detect(probe_text)
                    matches = meta.get('thanglish_matches', 0)
                    if text_lang == "tanglish" and matches >= THANGLISH_OVERRIDE_THRESHOLD:
                        logger.info(
                            f"[DETECT] English audio with {matches} Thanglish markers "
                            f"(≥{THANGLISH_OVERRIDE_THRESHOLD}) → 'tanglish' mode"
                        )
                        return "tanglish", "en"
                    elif text_lang == "tanglish":
                        logger.info(
                            f"[DETECT] English audio — only {matches} Thanglish markers "
                            f"(threshold={THANGLISH_OVERRIDE_THRESHOLD}), treating as English"
                        )

                logger.info("[DETECT] English detected → 'en' mode")
                return "en", "en"

            else:
                # Unknown/unsupported language (e.g., Hindi, Telugu, or Whisper-reported 'arabic')
                # Map known languages to ISO 639-1 codes
                language_map = {
                    'arabic': 'ar',
                    'ar': 'ar',
                    'tamil': 'ta',
                    'ta': 'ta',
                }
                
                if whisper_detected.lower() in language_map:
                    mapped_lang = language_map[whisper_detected.lower()]
                    logger.info(f"[DETECT] Whisper detected '{whisper_detected}' → mapped to '{mapped_lang}'")
                    return mapped_lang, mapped_lang
                
                # Try text detection on probe output as fallback
                if self.lang_detector and probe_text:
                    text_lang, _ = self.lang_detector.detect(probe_text)
                    logger.info(f"[DETECT] Unknown Whisper lang '{whisper_detected}', "
                                f"text detector says '{text_lang}' → using '{text_lang}'")
                    whisper_api_lang = "ta" if text_lang == "ta" else "ar" if text_lang == "ar" else "en"
                    return text_lang, whisper_api_lang

                logger.warning(f"[DETECT] Unrecognized language '{whisper_detected}', defaulting to English")
                return "en", "en"

        except Exception as e:
            logger.warning(f"[DETECT] Language probe failed: {e} — defaulting to multilingual mode")
            # Fallback: no language hint, use Thanglish-aware prompt
            return "tanglish", None

    # ── Transcription helpers ──────────────────────────────────────────────────

    def _transcribe_with_language(self, audio_path: str, detected_lang: str,
                                   whisper_lang: Optional[str]) -> Optional[str]:
        """
        Perform the actual Whisper transcription with the correct language + prompt.

        Args:
            audio_path:    Path to audio file
            detected_lang: 'en', 'ta', or 'tanglish'
            whisper_lang:  Whisper API language code, or None for auto
        """
        prompt = self.PROMPTS.get(detected_lang, self.PROMPTS["en"])

        logger.info(f"[WHISPER] Transcribing as '{detected_lang}' "
                    f"(whisper_lang={whisper_lang!r})")

        kwargs = {
            "file": None,  # set in context manager below
            "model": "whisper-1",
            "prompt": prompt,
        }
        if whisper_lang:  # None means no language hint (auto)
            kwargs["language"] = whisper_lang

        # For Tamil: request translation to English (Tamil → English is needed)
        if detected_lang == "ta":
            try:
                with open(audio_path, "rb") as audio_file:
                    response = self.client.audio.translations.create(
                        file=audio_file,
                        model="whisper-1",
                        # Keep prompt short and non-instructional to avoid echo
                        prompt="Medical consultation. Drug names and dosages.",
                    )
                text = response.text.strip()
                # Strip any prompt-echo artifacts from the beginning
                text = self._strip_prompt_echo(text)
                logger.info(f"[WHISPER] Tamil → English translation: {len(text)} chars")
                return text
            except Exception as e:
                logger.warning(f"[WHISPER] Translation failed: {e} — falling back to transcription")
                # Fall through to standard transcription below
                kwargs["language"] = "ta"
        
        # For Arabic: Use TRANSCRIPTION (not translation) - Groq understands Arabic well
        # Translation step was harmful, causing 'pulmonary' instead of 'sinusitis'
        elif detected_lang == "ar":
            kwargs["language"] = "ar"
            logger.info(f"[WHISPER] Arabic transcription (native): using 'ar' language code")
            # Continue to standard transcription below with Arabic language hint

        # Standard transcription (English / Thanglish)
        with open(audio_path, "rb") as audio_file:
            kwargs["file"] = audio_file
            response = self.client.audio.transcriptions.create(**kwargs)

        text = response.text.strip() if response.text else None
        # Strip any prompt-echo that Whisper may have prepended
        if text and detected_lang == "tanglish":
            text = self._strip_prompt_echo(text)
        return text

    def _strip_prompt_echo(self, text: str) -> str:
        """
        Remove Whisper prompt-echo artifacts from the start of translation output.

        Whisper sometimes prefixes the output with text from the prompt like:
          "Translate to English. Translate to Malayalam. If you have..."

        This strips those echo patterns, leaving only the real medical content.
        """
        if not text:
            return text

        # Lines that are pure meta/instruction echoes (not real content)
        ECHO_PATTERNS = [
            r'^translate\s+to\s+\w+[.,]?\s*',
            r'^translation[:\s]+',
            r'^english\s+translation[:\s]+',
            r'^medical\s+consultation[.,]?\s*',
            r'^doctor\s+prescribing[^.]*\.\s*',
            r'^drug\s+names[^.]*\.\s*',
            r'^transcribe\s+exactly\s+as\s+spoken[.,]?\s*',
            r'^patient\s+name[,\s]+diagnosis[^.]*\.\s*',
        ]

        import re as _re
        cleaned = text

        # Repeatedly strip echo lines from the beginning (handles multiple echoed sentences)
        changed = True
        while changed:
            changed = False
            for pattern in ECHO_PATTERNS:
                new = _re.sub(pattern, '', cleaned, flags=_re.IGNORECASE).strip()
                if new != cleaned:
                    cleaned = new
                    changed = True

        if cleaned != text:
            logger.info(f"[CLEAN] Stripped prompt echo: removed {len(text) - len(cleaned)} chars from start")

        return cleaned if cleaned else text  # fallback to original if we over-stripped

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _quality_ok(self, text: str) -> bool:
        """Check if transcript has minimum content."""
        words = len(text.split())
        if words < self.MIN_WORDS:
            logger.warning(f"[QUALITY] Low word count: {words} words (need >={self.MIN_WORDS})")
            return False

        text_lower = text.lower()
        has_medical = any(kw in text_lower for kw in self.MEDICAL_KEYWORDS)
        if not has_medical:
            logger.warning("[QUALITY] No medical keywords detected")
        return True

    def _build_result(self, text: str, detected_lang: str = "en",
                      whisper_lang: str = "en") -> TranscriptionResult:
        """Package result into standard format."""
        text = text.strip()
        confidence = 0.92  # OpenAI Whisper is highly reliable

        logger.info(
            f"[OK] Transcribed ({len(text)} chars, {len(text.split())} words) "
            f"[lang={detected_lang}]"
        )

        return TranscriptionResult(
            success=True,
            text=text,
            whisper_language=whisper_lang or "auto",
            detected_language=detected_lang,
            confidence=confidence,
            transcription_tier=1,
            cleaned_length=len(text),
        )
