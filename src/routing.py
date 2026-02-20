"""
Routing Module: Intelligent extraction routing (Groq-first design).

AudioAnalyzer: Measures input characteristics (quality, completeness, language, keywords)
RouteSelector: Decides which extraction pipeline(s) to use based on analysis

GROQ-FIRST PHILOSOPHY:
- Use Groq as primary ANY time we have reasonable input (>100 words, confidence >0.6)
- Ensemble only for borderline cases
- Rules-only as final fallback (not preventive measure)
- Do NOT reject transcripts solely due to low keyword ratio
"""

import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)


class AudioAnalyzer:
    """
    Analyzes input characteristics to determine optimal extraction strategy.
    Measures: transcript quality, language confidence, completeness, audio metrics.
    """

    def __init__(self):
        self.MIN_TRANSCRIPT_LENGTH = 20
        self.MIN_MEDICAL_KEYWORDS = 2
        self.MEDICAL_KEYWORDS = {
            'medicine', 'drug', 'tablet', 'pill', 'dose', 'mg', 'ml',
            'fever', 'pain', 'infection', 'doctor', 'patient', 'treatment',
            'cough', 'throat', 'cold', 'allergy', 'diagnosis', 'symptom',
            'antibiotic', 'infection', 'bacterial', 'daily', 'prescribe',
        }

    def analyze(self, transcript: str, whisper_confidence: float,
                language: str, language_confidence: float) -> Dict[str, Any]:
        """
        Analyze input and return routing metrics.
        Returns detailed analysis for RouteSelector decision-making.
        """
        metrics = {
            'transcript_quality': self._assess_transcript_quality(transcript),
            'completeness': self._assess_completeness(transcript),
            'language_clarity': language_confidence,
            'whisper_confidence': whisper_confidence,
            'detected_language': language,
            'has_medical_keywords': self._has_medical_keywords(transcript),
            'transcript_length': len(transcript),
            'word_count': len(transcript.split()),
        }

        # Calculate overall input quality score (0.0-1.0)
        metrics['overall_quality'] = (
            metrics['transcript_quality'] * 0.35 +
            metrics['completeness'] * 0.25 +
            metrics['language_clarity'] * 0.25 +
            metrics['whisper_confidence'] * 0.15
        )

        logger.info(f"Audio Analysis: Quality={metrics['overall_quality']:.0%}, "
                   f"Language={language}({language_confidence:.0%}), "
                   f"Length={metrics['transcript_length']} chars, "
                   f"Words={metrics['word_count']}")

        return metrics

    def _assess_transcript_quality(self, transcript: str) -> float:
        """Assess transcript quality (0.0-1.0)."""
        if len(transcript) < self.MIN_TRANSCRIPT_LENGTH:
            return 0.2

        words = transcript.split()
        if len(words) > 0:
            unique_ratio = len(set(words)) / len(words)
        else:
            unique_ratio = 0

        sentence_count = max(1, transcript.count('.') + transcript.count('?') + transcript.count('!'))
        sentence_avg_length = len(words) / sentence_count if sentence_count > 0 else 0

        quality = min(1.0, (unique_ratio * 0.6 + min(sentence_avg_length / 20, 1.0) * 0.4))
        return quality

    def _assess_completeness(self, transcript: str) -> float:
        """Assess transcript completeness based on length."""
        if len(transcript) < 50:
            return 0.2
        elif len(transcript) < 150:
            return 0.5
        elif len(transcript) < 400:
            return 0.8
        else:
            return 1.0

    def _has_medical_keywords(self, transcript: str) -> float:
        """Check presence of medical keywords (0.0-1.0)."""
        text_lower = transcript.lower()
        found_count = sum(1 for kw in self.MEDICAL_KEYWORDS if kw in text_lower)
        return min(1.0, found_count / max(1, len(self.MEDICAL_KEYWORDS)))


class RouteSelector:
    """
    Decides which extraction pipeline(s) to use based on input characteristics.
    
    Groq-First Philosophy:
    - 'groq_only': Good input (>100 words, conf>0.6) → Use Groq directly
    - 'ensemble': Borderline input → Use Groq + Rules voting
    - 'rules_only': Actual failures → Last resort
    
    DO NOT reject transcripts solely due to low keyword ratio.
    Trust that Groq can handle challenging inputs.
    """

    # Thresholds for Groq vs Ensemble vs Rules
    GROQ_MIN_WORDS = 100
    GROQ_MIN_CONFIDENCE = 0.6
    ENSEMBLE_MIN_WORDS = 50
    ENSEMBLE_MIN_CONFIDENCE = 0.4

    def __init__(self):
        pass

    def select_route(self, metrics: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Select routing strategy based on input metrics.
        Returns: (route_type, routing_config)
        
        Decision tree:
        1. If transcript > 100 words AND confidence > 0.6 → GROQ_ONLY (fast, direct)
        2. If transcript > 50 words AND confidence > 0.4 → ENSEMBLE (voting)
        3. Otherwise → RULES_ONLY (fallback)
        """
        quality = metrics['overall_quality']
        language = metrics['detected_language']
        word_count = metrics['word_count']
        confidence = metrics['whisper_confidence']
        transcript_len = metrics['transcript_length']

        logger.info(f"Routing Decision: quality={quality:.0%}, words={word_count}, "
                   f"confidence={confidence:.0%}, language={language}")

        # 🔥 SAFETY CHECK: If transcription is extremely bad (< 5 words), don't even try extraction
        if word_count < 5:
            logger.warning(f"[CRITICAL] Transcription failed (only {word_count} words) - likely corrupted/missing audio")
            logger.warning("[CRITICAL] Returning empty prescription (data quality too poor)")
            route = 'corrupted_audio'
            logger.info("[CRITICAL] CORRUPTED-AUDIO: Transcription produced almost nothing")

        # GROQ-FIRST: Good input → use Groq directly
        elif word_count >= self.GROQ_MIN_WORDS and confidence >= self.GROQ_MIN_CONFIDENCE:
            route = 'groq_only'
            logger.info("[OK] GROQ-FIRST: Good input → Using Groq (primary, fastest)")

        # ENSEMBLE: Borderline input → vote between Groq and Rules
        elif word_count >= self.ENSEMBLE_MIN_WORDS and confidence >= self.ENSEMBLE_MIN_CONFIDENCE:
            route = 'ensemble'
            logger.info("[UNCERTAIN] ENSEMBLE: Borderline input → Using Groq + Rules (voting)")

        # RULES-ONLY: Poor input → fallback to rules
        else:
            route = 'rules_only'
            logger.warning(f"[FALLBACK] RULES-ONLY: Poor input (words={word_count}, conf={confidence:.0%})")

        return route, {
            'quality_score': quality,
            'language': language,
            'word_count': word_count,
            'confidence': confidence,
            'transcript_length': transcript_len,
        }

