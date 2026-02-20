"""
Thanglish Normalization Module: Convert Thanglish (Tamil written in English letters) to Tamil.

Used when language detected as "tanglish" to normalize transcripts before extraction.
"""

import logging
import re
from typing import Tuple, Dict

logger = logging.getLogger(__name__)


class ThanglishNormalizer:
    """Convert Thanglish transliterations to Tamil Unicode"""

    # Comprehensive Thanglish → Tamil mapping
    THANGLISH_MAP = {
        # Common words
        'noi': 'நோய்',              # disease
        'sayanam': 'சயனம்',        # lying down
        'marunthu': 'மருந்து',      # medicine
        'vali': 'வலி',              # pain
        'kaichal': 'காய்ச்சல்',     # fever
        'sapadu': 'சாப்பாடு',       # food/eat
        'kaalai': 'காலை',          # morning
        'iravu': 'இரவு',           # night
        'oru': 'ஒரு',              # one/a
        'rangu': 'ரங்கு',          # stage
        'maaram': 'மாரம்',         # chest
        
        # Medical terms
        'heart': 'இருதயம்',        # heart (anglicized cognate)
        'kaasai': 'இருமல்',        # cough
        'throatil': 'தொண்டையில்',  # in throat
        
        # Multipliers/Numbers (transliterated)
        'ondru': 'ஒன்று',          # one
        'randu': 'ரண்டு',          # two
        'munnu': 'முன்னூ',         # three
        'naanu': 'நான்கு',         # four
        'aynu': 'ஐந்து',           # five
        
        # Frequency/Time
        'neram': 'நேரம்',          # time
        'nerattai': 'நேரத்தை',     # time (accusative)
        'matrn': 'மாலை',          # evening
        'pkal': 'பகல்',            # day
        'inru': 'இன்று',           # today
        'netru': 'நெய்து',         # yesterday
        
        # General medical
        'doctor': 'டாக்டர்',        # doctor
        'uravai': 'உறுப்பு',        # organ
        'payir': 'பயிர்',          # affecting
        'payanam': 'பயணம்',        # journey/spread
        'vaalkai': 'வாழ்க்கை',     # life
        'noimai': 'நோயுறுதல்',     # sickness
    }

    # Phonetic pattern rules (advanced)
    PHONETIC_RULES = {
        # Aspirated sounds
        r'\bth([a-z])': r'த\1',     # th* → த*
        r'\bkh([a-z])': r'க\1',     # kh* → க*
        r'\bph([a-z])': r'ப\1',     # ph* → ப*
        
        # Retroflex sounds
        r'\btt([a-z])': r'ட\1',     # tt* → ட*
        r'\bnn([a-z])': r'ண\1',     # nn* → ண*
        r'\bll([a-z])': r'ள\1',     # ll* → ள*
        
        # Common endings
        r'ai$': 'ை',               # ai → ை
        r'u$': 'ு',                # u → ு
        r'o$': 'ோ',               # o → ோ
    }

    def normalize(self, text: str) -> Tuple[str, bool]:
        """
        Normalize Thanglish to Tamil representation.
        
        Strategy:
        1. Direct lookup in THANGLISH_MAP
        2. Apply phonetic rules
        3. Keep unrecognized English words as-is (likely proper nouns or English cognates)
        
        Returns:
            (normalized_text, was_modified)
        """
        if not text or not isinstance(text, str):
            return text, False

        original = text
        result = text.lower()

        # Apply direct mappings (word boundary)
        for thanglish, tamil in sorted(self.THANGLISH_MAP.items(), key=lambda x: -len(x[0])):
            pattern = r'\b' + re.escape(thanglish) + r'\b'
            result = re.sub(pattern, tamil, result, flags=re.IGNORECASE)

        # Apply phonetic rules (more advanced, optional)
        # Disabled for now to avoid over-correction
        # for pattern, replacement in self.PHONETIC_RULES.items():
        #     result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        was_modified = result.lower() != original.lower()

        if was_modified:
            logger.info(f"[THANGLISH] Normalized: {len(original)} chars → {len(result)} chars")
        else:
            logger.info("[THANGLISH] No Thanglish terms found for normalization")

        return result, was_modified

    def to_structured_tokens(self, text: str) -> Dict[str, any]:
        """
        Alternative: Convert Thanglish to structured tokens instead of Tamil Unicode.
        Useful for systems that may not handle Tamil fonts well.
        
        Returns dict of medical entities with original + normalized forms
        """
        tokens = {
            'medicines': [],
            'symptoms': [],
            'frequency': [],
            'time_of_day': [],
            'other': []
        }

        # Extract and categorize
        text_lower = text.lower()

        # Medical categories
        medicine_terms = ['marunthu', 'medicine', 'tablet', 'pill', 'kanam']
        symptom_terms = ['vali', 'kaichal', 'noi', 'cough', 'throat', 'sore']
        frequency_terms = ['ondru', 'randu', 'munnu', 'naanu', 'matrn', 'kaalai', 'iravu']

        for term in medicine_terms:
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, text_lower, re.IGNORECASE):
                tokens['medicines'].append({
                    'original': term,
                    'tamil': self.THANGLISH_MAP.get(term, term)
                })

        for term in symptom_terms:
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, text_lower, re.IGNORECASE):
                tokens['symptoms'].append({
                    'original': term,
                    'tamil': self.THANGLISH_MAP.get(term, term)
                })

        for term in frequency_terms:
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, text_lower, re.IGNORECASE):
                tokens['frequency'].append({
                    'original': term,
                    'tamil': self.THANGLISH_MAP.get(term, term)
                })

        return tokens
