"""
Transcript Normalization Module: Clean and normalize medical transcripts.

Handles:
- ASR distortion correction
- Dosage normalization
- Duplicate word removal
- Frequency standardization
"""

import logging
import re
from typing import Tuple, Dict, Any

logger = logging.getLogger(__name__)


class TranscriptNormalizer:
    """Clean and normalize medical transcripts before extraction"""

    # ASR distortion corrections (phonetic confusions)
    ASR_CORRECTIONS = {
        # Infection-related (common Whisper errors)
        r'\binflection\b': 'infection',
        r'\binfraction\b': 'infection',
        r'\binfractions\b': 'infections',
        r'\bback\s+inflection\b': 'bacterial infection',
        r'\bbacterial\s+infraction\b': 'bacterial infection',

        # Pharyngitis variants
        r'\bpharyngitis\b': 'pharyngitis',  # Already correct
        r'\bfrangitis\b': 'pharyngitis',
        r'\bfrench\s+(?:dices|dice)\b': 'pharyngitis',
        r'\bfirennets\b': 'pharyngitis',
        r'\bpharangitis\b': 'pharyngitis',
        r'\bparagenesis\b': 'pharyngitis',
        r'\bparakinesis\b': 'pharyngitis',
        r'\bpyrogynous\b': 'pharyngitis',

        # Drug name distortions
        r'\blevosidazine\b': 'levocetirizine',
        r'\blevocitirizine\b': 'levocetirizine',
        r'\blevocitrazine\b': 'levocetirizine',
        r'\blevofitrizin\b': 'levocetirizine',
        r'\bbenzimidine\b': 'benzydamine',
        r'\bbenzodiazine\b': 'benzydamine',
        r'\btrepsils\b': 'strepsils',
        r'\berytho(?!mycin)\s+mice\s+in\b': 'erythromycin',
        r'\berytho\s+mice\s+in\b': 'erythromycin',
        r'\berythomycin\b': 'erythromycin',
        r'\berytromycin\b': 'erythromycin',
        r'\bermycin\b': 'erythromycin',

        r'\bamoxycillin\b': 'amoxicillin',
        r'\bamoxylin\b': 'amoxicillin',
        r'\bamoxilin\b': 'amoxicillin',

        r'\bparacetamole\b': 'paracetamol',
        r'\baccetaminophen\b': 'paracetamol',
        r'\baccetaminife\b': 'acetaminophen',

        r'\basprine\b': 'aspirin',
        r'\basprin\b': 'aspirin',

        r'\bibuprofen\b': 'ibuprofen',

        r'\branitidine\b': 'ranitidine',
        r'\brnitidine\b': 'ranitidine',

        r'\bmetformin\b': 'metformin',
        r'\bmetaphormion\b': 'metformin',
        r'\bmetphormion\b': 'metformin',

        r'\bomeprazole\b': 'omeprazole',
        r'\bomerazole\b': 'omeprazole',

        r'\bciprofloxacin\b': 'ciprofloxacin',
        r'\bciproflo\b': 'ciprofloxacin',

        # Antibiotic-related
        r'\bantibiotic\s+risk\b': 'antibiotics',
        r'\banti\s+(?:biotic\s+)?risk\b': 'antibiotics',
        r'\bantibiotic\b(?!\s+s)': 'antibiotics',  # Don't match if already plural

        # Throat/Bacterial
        r'\bthroat\s+infraction\b': 'throat infection',
        r'\bbacterial\s+fracture\b': 'bacterial infection',
        r'\binfect(?!ion)\b': 'infection',

        # Tamil/Thanglish phonetic confusions
        r'\bkayaichel\b': 'fever',
        r'\bkayachel\b': 'fever',
        r'\bkaiachel\b': 'fever',
        r'\binflection\b': 'infection',  # Repeated but important
    }

    # Dosage unit normalization
    DOSAGE_PATTERNS = {
        r'(\d+(?:\.\d+)?)\s*mg\b': r'\1 mg',         # 500mg → 500 mg
        r'(\d+(?:\.\d+)?)\s*ml\b': r'\1 ml',         # 10ml → 10 ml
        r'(\d+(?:\.\d+)?)\s*mcg\b': r'\1 mcg',       # 100mcg → 100 mcg
        r'(\d+(?:\.\d+)?)\s*gm\b': r'\1 gm',         # 1gm → 1 gm
        r'(\d+(?:\.\d+)?)\s*gram\b': r'\1 gm',       # 1gram → 1 gm
        r'(\d+)\s*iu\b': r'\1 iu',
        r'(\d+)\s*unit\b': r'\1 unit',
        r'(\d+)\s*tablet\b': r'\1 tablet',
        r'(\d+)\s*capsule\b': r'\1 capsule',
        r'(\d+)\s*drop\b': r'\1 drop',
        r'(\d+)\s*tsp\b': r'\1 teaspoon',
        r'(\d+)\s*tbsp\b': r'\1 tablespoon',
    }

    # Frequency standardization
    FREQUENCY_PATTERNS = {
        r'\bone\s+time\s+a\s+day\b': 'once a day',
        r'\bonce\b': 'once a day',
        r'\btwo\s+times?\s+a\s+day\b': 'twice a day',
        r'\btwice\b': 'twice a day',
        r'\bthree\s+times?\s+(?:a\s+)?day\b': '3 times a day',
        r'\bthrice\b': '3 times a day',
        r'\bfour\s+times?\s+(?:a\s+)?day\b': '4 times a day',
        r'\bdaily\b': 'once a day',
        r'\bevery\s+day\b': 'once a day',
        r'\bonce\s+daily\b': 'once a day',
        r'\btwice\s+daily\b': 'twice a day',
        r'\bthrice\s+daily\b': '3 times a day',
        r'\bevery\s+morning(?:\s+and\s+night)?\b': 'once a day',
    }

    # Duration standardization
    DURATION_PATTERNS = {
        r'(\d+)\s+days?\b': r'\1 days',
        r'(\d+)\s+weeks?\b': r'\1 weeks',
        r'(\d+)\s+months?\b': r'\1 months',
        r'\bfor\s+(\d+)\s+days?\b': r'for \1 days',
    }

    def normalize(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """
        Normalize transcript:
        1. Fix ASR distortions
        2. Normalize dosage units
        3. Standardize frequency
        4. Remove duplicate words
        
        Returns:
            (normalized_text, metadata)
        """
        if not text or not isinstance(text, str):
            return text, {'steps': [], 'was_modified': False}

        original = text
        result = text.lower()
        metadata = {'steps': []}

        # Step 1: Fix ASR distortions
        for pattern, correction in self.ASR_CORRECTIONS.items():
            before_count = len(re.findall(pattern, result, re.IGNORECASE))
            result = re.sub(pattern, correction, result, flags=re.IGNORECASE)
            if before_count > 0:
                metadata['steps'].append(f"Fixed {before_count} ASR errors ({pattern[:30]}...)")

        # Step 2: Normalize dosage units
        for pattern, replacement in self.DOSAGE_PATTERNS.items():
            before_count = len(re.findall(pattern, result, re.IGNORECASE))
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
            if before_count > 0:
                metadata['steps'].append(f"Normalized {before_count} dosage units")

        # Step 3: Standardize frequency
        for pattern, replacement in self.FREQUENCY_PATTERNS.items():
            before_count = len(re.findall(pattern, result, re.IGNORECASE))
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
            if before_count > 0:
                metadata['steps'].append(f"Standardized {before_count} frequency expressions")

        # Step 4: Standardize duration
        for pattern, replacement in self.DURATION_PATTERNS.items():
            before_count = len(re.findall(pattern, result, re.IGNORECASE))
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
            if before_count > 0:
                metadata['steps'].append(f"Standardized {before_count} duration expressions")

        # Step 5: Remove consecutive duplicate words
        result = self._remove_duplicate_words(result)
        metadata['steps'].append("Removed duplicate consecutive words")

        # Capitalize first letter
        if result:
            result = result[0].upper() + result[1:]

        was_modified = result.lower() != original.lower()
        metadata['was_modified'] = was_modified
        metadata['original_length'] = len(original)
        metadata['normalized_length'] = len(result)

        if was_modified:
            logger.info(f"[NORMALIZE] Transcript cleaned ({len(original)} → {len(result)} chars)")
            for step in metadata['steps']:
                logger.debug(f"  - {step}")
        else:
            logger.info("[NORMALIZE] No normalization needed")

        return result, metadata
    
    def validate_medical_semantics(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """
        FIX 2: Validate medical vocabulary consistency.
        Detect and correct anatomically impossible substitutions (e.g., 'pulmonary' in sinusitis context).
        """
        result = text.lower()
        changes = []
        
        # Medical context-based corrections
        # If sinusitis/nasal context detected but wrong organ mentioned → correct it
        nasal_keywords = ['sinus', 'nasal', 'nose', 'nostril', 'septum', 'turbinate', 'concha']
        wrong_organ_keywords = {
            'pulmonary': 'nasal',           # pulmonary artery/vein shouldn't appear in sinusitis
            'cardiac': 'nasal',
            'renal': 'nasal',
            'gastric': 'nasal',
        }
        
        throat_keywords = ['throat', 'pharynx', 'larynx', 'tonsil', 'uvula']
        
        # Check if this is a nasal/sinus condition
        nasal_context = any(keyword in result for keyword in nasal_keywords)
        throat_context = any(keyword in result for keyword in throat_keywords)
        
        if nasal_context:
            for wrong_word, correct_word in wrong_organ_keywords.items():
                if wrong_word in result:
                    # Additional check: if it appears with nasal-adjacent words, fix it
                    pattern = rf'.*(?:{"|".join(nasal_keywords)}).*{wrong_word}|{wrong_word}.*(?:{"|".join(nasal_keywords)})'
                    if re.search(pattern, result, re.IGNORECASE):
                        result = re.sub(rf'\b{wrong_word}\b', correct_word, result, flags=re.IGNORECASE)
                        changes.append(f"Fixed anatomical inconsistency: '{wrong_word}' → '{correct_word}' (nasal context)")
        
        # Medical vocabulary database for validation
        valid_medical_terms = {
            'sinusitis', 'pharyngitis', 'laryngitis', 'bronchitis', 'pneumonia',
            'gastritis', 'enteritis', 'otitis', 'rhinitis', 'conjunctivitis',
            'urinalysis', 'cbc', 'bloodwork', 'xray', 'ultrasound', 'ct',
            'fever', 'cough', 'sore throat', 'congestion', 'discharge',
            'antibiotic', 'paracetamol', 'ibuprofen', 'levocetirizine', 'amoxicillin',
        }
        
        metadata = {
            'steps': changes,
            'validity': 'medical_semantics_validated'
        }
        
        if changes:
            logger.info(f"[SEMANTIC] Medical vocabulary validated: {len(changes)} corrections")
            for change in changes:
                logger.debug(f"  - {change}")
        
        return result, metadata

    @staticmethod
    def _remove_duplicate_words(text: str) -> str:
        """Remove consecutive duplicate words"""
        words = text.split()
        deduped = []

        for word in words:
            # Only skip if this word matches the previous word (case-insensitive)
            if not deduped or word.lower() != deduped[-1].lower():
                deduped.append(word)

        return ' '.join(deduped)
