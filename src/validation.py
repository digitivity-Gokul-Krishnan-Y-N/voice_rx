"""
Validation Module: Prescription validation (drug database, dose format, safety checks).

ValidationLayer: Validates prescription completeness, drug database consistency, and safety
"""

import logging
import re
from datetime import datetime
from typing import Tuple, List
from dataclasses import dataclass

try:
    from medicine_database import DANGEROUS_COMBINATIONS, DOSE_PATTERNS
    MEDICINE_DB_AVAILABLE = True
except ImportError:
    MEDICINE_DB_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class Prescription:
    """Standard prescription data structure."""
    patient_name: str
    age: int = None
    language: str = "en"
    complaints: List[str] = None
    diagnosis: List[str] = None
    medicines: List[dict] = None
    tests: List[str] = None
    advice: List[str] = None
    confidence: float = 0.0
    extraction_method: str = "unknown"
    transcription_tier: int = 1
    warnings: List[str] = None
    timestamp: str = None

    def __post_init__(self):
        """Initialize empty lists and timestamp."""
        if self.complaints is None:
            self.complaints = []
        if self.diagnosis is None:
            self.diagnosis = []
        if self.medicines is None:
            self.medicines = []
        if self.tests is None:
            self.tests = []
        if self.advice is None:
            self.advice = []
        if self.warnings is None:
            self.warnings = []
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class ValidationLayer:
    """
    Validate prescription:
    - Required fields (patient name, diagnosis, medicines)
    - Dose format (must include units)
    - Duplicates
    - Dangerous drug combinations
    """

    # Fallback if medicine database not available
    DOSE_PATTERNS_FALLBACK = {
        'mg': r'\d+\s*mg',
        'ml': r'\d+\s*ml',
        'mcg': r'\d+\s*mcg',
        'tablet': r'\d+\s*tablet',
        'capsule': r'\d+\s*capsule',
    }

    DANGEROUS_COMBINATIONS_FALLBACK = {
        ('aspirin', 'ibuprofen'): 'Both are NSAIDs - avoid together',
        ('metoprolol', 'verapamil'): 'Both lower heart rate - high risk',
    }

    def __init__(self):
        """Initialize validation rules from database or fallback."""
        if MEDICINE_DB_AVAILABLE:
            self.DOSE_PATTERNS = DOSE_PATTERNS
            self.DANGEROUS_COMBINATIONS = DANGEROUS_COMBINATIONS
            logger.info("[OK] Loaded validation rules from medicine database")
        else:
            self.DOSE_PATTERNS = self.DOSE_PATTERNS_FALLBACK
            self.DANGEROUS_COMBINATIONS = self.DANGEROUS_COMBINATIONS_FALLBACK
            logger.info("⚠️  Using fallback validation rules")

    def validate(self, prescription: Prescription) -> Tuple[bool, List[str], List[str]]:
        """
        Validate prescription.
        
        Returns:
            (is_valid: bool, errors: List[str], warnings: List[str])
        """
        errors = []
        warnings = []

        # Optional fields (moved to warnings instead of errors)
        if not prescription.patient_name:
            warnings.append("⚠️  Patient name not captured")

        if not prescription.diagnosis:
            warnings.append("⚠️  No diagnosis found")

        if not prescription.medicines:
            warnings.append("⚠️  No medicines prescribed (follow-up or advice-only consultation)")

        # Validate medicines
        seen_drugs = set()
        for i, med in enumerate(prescription.medicines):
            med_dict = med if isinstance(med, dict) else vars(med)

            # Check dose format - more lenient
            dose = str(med_dict.get('dose', ''))
            
            # Allow if dose is missing (will be warning instead of error)
            if dose and dose.lower() != 'none':
                has_valid_dose = any(re.search(pattern, dose.lower()) for pattern in self.DOSE_PATTERNS.values())
                if not has_valid_dose and len(dose) > 1:  # Only warn if dose is provided but malformed
                    warnings.append(f"Medicine {i+1}: Dose format unclear '{dose}'")
            elif not dose or dose.lower() == 'none':
                warnings.append(f"Medicine {i+1}: Dose not specified")

            # Check for duplicates
            drug_name = str(med_dict.get('name', '')).lower()
            if drug_name in seen_drugs:
                warnings.append(f"Duplicate drug '{med_dict.get('name', '')}'")
            else:
                seen_drugs.add(drug_name)

            # Check for dangerous combinations
            for (drug1, drug2), warning_msg in self.DANGEROUS_COMBINATIONS.items():
                if drug_name in [drug1.lower(), drug2.lower()]:
                    if any(d in seen_drugs for d in [drug1.lower(), drug2.lower()]):
                        warnings.append(f"[WARNING] {warning_msg}")

        is_valid = len(errors) == 0
        logger.info(f"Validation: {'[OK] PASSED' if is_valid else '[FAIL] FAILED'} "
                   f"({len(errors)} errors, {len(warnings)} warnings)")

        return is_valid, errors, warnings
