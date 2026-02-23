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
        # Nouns - medical
        'noi': 'disease',
        'marunthu': 'medicine',
        'vali': 'pain',
        'kaichal': 'fever',
        'kayachel': 'fever',
        'kaiachel': 'fever',
        'sapadu': 'food',
        'kaalai': 'morning',
        'iravu': 'night',
        'oru': 'one',
        'maaram': 'chest',
        'usna': 'heat',
        'moolai': 'brain',
        'kai': 'hand',
        'kan': 'eye',
        'siram': 'head',
        'mookkadaippu': 'nasal congestion',
        # Verbs / Action words (very common in Thanglish)
        'pannu': 'do/use',
        'pannalam': 'can do',
        'pannalaam': 'can do',
        'panna': 'to do',
        'panren': 'I suggest/do',
        'eduthukko': 'take it',
        'edukkalaam': 'can take',
        'kudichuko': 'drink it',
        'kurichiko': 'drink it',
        'varalam': 'may come/have',
        'varalaam': 'may come/have',
        'varum': 'will come',
        'agum': 'will become',
        'agam': 'will become',
        'aagum': 'will become',
        'agavam': 'to become',
        'aagavum': 'to help become',
        'irukku': 'is/has',
        'irundha': 'if there is',
        'irukkura': 'existing',
        # Connectors / prepositions
        'appram': 'after',
        'apram': 'after',
        'la': 'in/at',
        'idhu': 'this',
        'idu': 'this',
        'idaku': 'for this',
        'adhanala': 'because of that',
        'maadhiri': 'like/similar',
        'madhuri': 'like/similar',
        'nala': 'for/due to',
        'nerea': 'a lot',
        'neraya': 'a lot',
        'konjam': 'a little',
        'kammi': 'reduce/less',
        'kami': 'reduce',
        'romba': 'very',
        'illa': 'or/no',
        'illana': 'otherwise',
        'silla': 'some',
        'sila': 'some',
        'naal': 'days',
        'naalu': 'days/four',
        'udane': 'immediately',
        'aana': 'but/after',
        'ana': 'but',
        'koodadhu': 'should not',
        'kudadu': 'should not',
        'nallu': 'good',
        'pakkathula': 'near/side',
        'unakku': 'to you',
        'unatku': 'to you',
        'thoonguna': 'sleeping',
        'thunguna': 'sleeping',
        'elevate': 'elevate',  # Used in Thanglish context: 'head elevate pannu'
        'confirm': 'confirm',
        'severity': 'severity',
        'severe': 'severe',
        'recurrent': 'recurrent',
        'follow': 'follow',
        'review': 'review',
        'contact': 'contact',
        'vaa': 'come',
        'mukhiyam': 'important',
    }

    # Thanglish patterns — verb suffixes and Tamil transliterations
    THANGLISH_PATTERNS = [
        r'\b(noi|marunthu|vali|kaichal|kayachel|kaiachel|sapadu|kaalai|iravu)\b',
        r'\b(pannu|pannalam|panna|panren|eduthukko|edukkalaam|kurichiko|kudichuko)\b',
        r'\b(varalam|varalaam|varum|agum|aagum|agavam|aagavum|irukku|irundha)\b',
        r'\b(apram|appram|adhanala|maadhiri|kammi|kami|romba|neraya|nerea|konjam)\b',
        r'\b(idhu|idu|idaku|unakku|udane|illana|koodadhu|kudadu|thoonguna|thunguna)\b',
        r'\b(naal|naalu|aana|ana|silla|sila|pakkathula|la\b)',  # short but distinctive
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
            # Tamil words + verbs in English + English text → Thanglish
            logger.info(f"[TANGLISH] Thanglish detected ({thanglish_matches} term matches)")
            return 'tanglish', {
                'confidence': min(0.95, 0.6 + thanglish_matches * 0.05),
                'thanglish_matches': thanglish_matches,
                'reason': f'Found {thanglish_matches} Thanglish indicators (verbs/terms)'
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
