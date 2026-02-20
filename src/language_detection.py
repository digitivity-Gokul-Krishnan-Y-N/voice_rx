"""
Language Detection Module: Detect English, Tamil, or Thanglish from transcript.

Supports:
- English: Pure English text
- Tamil: Tamil Unicode characters (>10% density)
- Thanglish: Tamil words written in English letters + English text
"""

import logging
import re
from typing import Tuple, Dict

logger = logging.getLogger(__name__)


class LanguageDetector:
    """Detect language: English, Tamil, or Thanglish"""

    # Tamil Unicode range
    TAMIL_RANGE = range(0x0B80, 0x0BFF)

    # Common Thanglish medical terms (Tamil words written in English)
    THANGLISH_MEDICAL_TERMS = {
        'noi': 'நோய்',              # disease
        'marunthu': 'மருந்து',       # medicine
        'vali': 'வலி',              # pain
        'kaichal': 'காய்ச்சல்',      # fever
        'kayachel': 'காய்ச்சல்',     # fever (variant)
        'kaiachel': 'காய்ச்சல்',     # fever (variant)
        'sapadu': 'சாப்பாடு',        # food
        'kaalai': 'காலை',           # morning
        'iravu': 'இரவு',            # night
        'oru': 'ஒரு',              # one
        'maaram': 'மாரம்',          # chest
        'usna': 'உஷ்ணம்',          # heat/fever
        'moolai': 'மூளை',          # brain
        'valiyal': 'வலிய',          # pain
        'puyasu': 'பூச்சு',          # allergy
        'kai': 'கை',               # hand
        'kan': 'கண்',              # eye
        'paathai': 'பாதம்',         # foot
        'siram': 'சிரம்',           # head
        'izhuppu': 'இழுப்பு',       # pulling pain
    }

    # Thanglish patterns (regex) - Tamil transliterations
    THANGLISH_PATTERNS = [
        r'\b(noi|marunthu|vali|kaichal|kayachel|kaiachel|sapadu|kaalai|iravu)\b',
        r'\b(oru|maaram|usna|moolai|valiyal|puyasu|kai|kan|paathai|siram|izhuppu)\b',
    ]

    def detect(self, text: str) -> Tuple[str, Dict[str, any]]:
        """
        Detect language: English, Tamil, or Thanglish
        
        Returns:
            (language_code: str, metadata: Dict)
            - language_code: 'en', 'ta', or 'tanglish'
            - metadata: confidence, character_ratio, matches found, etc.
        """
        if not text or not isinstance(text, str):
            return 'en', {'confidence': 0.0, 'reason': 'Empty text'}

        text_lower = text.lower()

        # Count Tamil characters
        tamil_char_count = sum(1 for char in text if ord(char) in self.TAMIL_RANGE)
        tamil_ratio = tamil_char_count / len(text) if text else 0

        # Check for Thanglish words
        thanglish_matches = self._count_thanglish_matches(text_lower)
        has_thanglish = thanglish_matches > 0

        # Decision logic
        if tamil_ratio > 0.1:
            # >10% Tamil characters → Tamil
            logger.info(f"[TA] Tamil detected ({tamil_ratio:.0%} characters)")
            return 'ta', {
                'confidence': min(1.0, tamil_ratio),
                'tamil_char_ratio': tamil_ratio,
                'reason': 'High Tamil character density'
            }

        elif has_thanglish and len(text) > 20:
            # Tamil words in English + English text → Thanglish
            logger.info(f"[TANGLISH] Thanglish detected ({thanglish_matches} term matches)")
            return 'tanglish', {
                'confidence': 0.8,
                'thanglish_matches': thanglish_matches,
                'reason': f'Found {thanglish_matches} Tamil transliteration terms'
            }

        else:
            # Default to English
            logger.info("[EN] English detected (default)")
            return 'en', {
                'confidence': 0.85,
                'tamil_ratio': tamil_ratio,
                'thanglish_matches': thanglish_matches,
                'reason': 'No Tamil/Thanglish indicators'
            }

    def _count_thanglish_matches(self, text_lower: str) -> int:
        """Count Thanglish medical terms in text"""
        count = 0

        # Check direct medical terms
        for term in self.THANGLISH_MEDICAL_TERMS.keys():
            # Use word boundary regex for more accurate matching
            pattern = r'\b' + re.escape(term) + r'\b'
            matches = len(re.findall(pattern, text_lower))
            count += matches

        # Check patterns
        for pattern in self.THANGLISH_PATTERNS:
            matches = len(re.findall(pattern, text_lower))
            count += matches

        return count

    def get_language_name(self, lang_code: str) -> str:
        """Get human-readable language name"""
        names = {
            'en': 'English',
            'ta': 'Tamil (Unicode)',
            'tanglish': 'Thanglish (Tamil in English script)'
        }
        return names.get(lang_code, 'Unknown')
