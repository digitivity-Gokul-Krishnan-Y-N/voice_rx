"""
ENHANCED VALIDATION LAYER - Production Grade
- Drug interaction database
- Dosage validation
- Age-based restrictions  
- Allergy conflict detection
- Contraindication checking
"""

import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)

@dataclass
class DrugInfo:
    """Complete drug information"""
    name: str
    generic_name: str
    category: str
    min_dose_mg: float
    max_dose_mg: float
    freq_min: int  # min times per day
    freq_max: int  # max times per day
    age_min: int = 0
    age_max: int = 150
    contraindications: List[str] = None
    side_effects: List[str] = None
    interactions: Dict[str, str] = None

# Hospital drug database (expandable)
DRUG_DATABASE = {
    'erythromycin': DrugInfo(
        name='Erythromycin',
        generic_name='erythromycin',
        category='Antibiotic (Macrolide)',
        min_dose_mg=250,
        max_dose_mg=1000,
        freq_min=1,
        freq_max=4,
        age_min=1,
        side_effects=['nausea', 'diarrhea', 'abdominal pain'],
        interactions={
            'warfarin': 'CRITICAL - increases INR',
            'theophylline': 'increases theophylline levels',
            'cisapride': 'CRITICAL - risk of arrhythmias'
        }
    ),
    'amoxicillin': DrugInfo(
        name='Amoxicillin',
        generic_name='amoxicillin',
        category='Antibiotic (Beta-lactam)',
        min_dose_mg=250,
        max_dose_mg=1000,
        freq_min=1,
        freq_max=3,
        age_min=1,
        side_effects=['rash', 'diarrhea', 'allergic reaction'],
        interactions={
            'warfarin': 'increases bleeding risk',
            'methotrexate': 'increases MTX toxicity'
        }
    ),
    'paracetamol': DrugInfo(
        name='Paracetamol',
        generic_name='acetaminophen',
        category='Analgesic/Antipyretic',
        min_dose_mg=500,
        max_dose_mg=4000,  # Max daily dose
        freq_min=1,
        freq_max=4,  # 4 times a day max for 4g/day total
        age_min=3,
        side_effects=['rare hepatotoxicity in overdose'],
        interactions={}
    ),
    'ibuprofen': DrugInfo(
        name='Ibuprofen',
        generic_name='ibuprofen',
        category='NSAID',
        min_dose_mg=200,
        max_dose_mg=800,
        freq_min=1,
        freq_max=3,
        age_min=6,
        side_effects=['GI bleeding', 'ulcers', 'kidney damage'],
        interactions={
            'aspirin': 'CRITICAL - increased GI bleed risk',
            'warfarin': 'increased bleeding risk',
            'methotrexate': 'increased toxicity'
        }
    ),
    'aspirin': DrugInfo(
        name='Aspirin',
        generic_name='acetylsalicylic acid',
        category='NSAID/Antiplatelet',
        min_dose_mg=75,
        max_dose_mg=1000,
        freq_min=1,
        freq_max=3,
        age_min=16,
        side_effects=['GI bleeding', 'allergy'],
        interactions={
            'ibuprofen': 'CRITICAL - increased GI bleed risk',
            'warfarin': 'increased bleeding'
        }
    ),
    'metformin': DrugInfo(
        name='Metformin',
        generic_name='metformin',
        category='Antidiabetic',
        min_dose_mg=500,
        max_dose_mg=2000,
        freq_min=1,
        freq_max=3,
        age_min=18,
        side_effects=['lactic acidosis (rare)', 'GI upset'],
        interactions={}
    ),
}

class EnhancedValidationLayer:
    """Production-grade validation"""
    
    def __init__(self):
        self.drug_db = DRUG_DATABASE
        self.validation_warnings = []
        
    def validate_prescription(self, patient_age: Optional[int], medicines: List, 
                             allergies: List[str] = None) -> Tuple[bool, List[str], List[str]]:
        """
        Comprehensive validation returning (is_valid, errors, warnings)
        """
        errors = []
        warnings = []
        allergies = allergies or []
        
        if not medicines:
            errors.append("At least one medicine required")
            return False, errors, warnings
        
        # Track what we're adding
        drug_names = [m.name.lower() for m in medicines]
        
        for i, med in enumerate(medicines):
            med_name = med.name.lower()
            
            # 1. Check if drug is in database
            drug_info = self._get_drug_info(med_name)
            
            if drug_info:
                # 2. Validate dose
                dose_errors = self._validate_dose(med, drug_info, i+1)
                errors.extend(dose_errors)
                
                # 3. Validate frequency
                freq_errors = self._validate_frequency(med, drug_info, i+1)
                errors.extend(freq_errors)
                
                # 4. Age-based validation
                if patient_age:
                    if patient_age < drug_info.age_min:
                        errors.append(f"Drug {i+1} ({med.name}): minimum age is {drug_info.age_min}")
                    elif patient_age > drug_info.age_max:
                        warnings.append(f"⚠️  Drug {i+1} ({med.name}): caution in ages >70")
                
                # 5. Allergy check
                if self._check_allergy_conflict(med_name, allergies):
                    errors.append(f"Drug {i+1}: ALLERGY CONFLICT - patient allergic to {med_name}")
                
                # 6. Contraindication check
                if self._has_contraindications(med_name, patient_age):
                    errors.append(f"Drug {i+1}: CONTRAINDICATED in this patient")
            else:
                warnings.append(f"⚠️  Drug {i+1} ({med.name}): NOT in hospital database - manual review needed")
        
        # 7. Drug-drug interactions
        interaction_warnings = self._check_interactions(medicines)
        warnings.extend(interaction_warnings)
        
        # 8. Duplicate check
        if len(drug_names) != len(set(drug_names)):
            errors.append("Duplicate medications found")
        
        return len(errors) == 0, errors, warnings
    
    def _get_drug_info(self, drug_name: str) -> Optional[DrugInfo]:
        """Lookup drug in database"""
        drug_key = drug_name.lower().strip()
        return self.drug_db.get(drug_key)
    
    def _validate_dose(self, medicine, drug_info: DrugInfo, med_num: int) -> List[str]:
        """Validate dose is within safe range"""
        errors = []
        
        # Extract numeric dose
        dose_match = re.search(r'(\d+(?:\.\d+)?)', medicine.dose)
        if not dose_match:
            errors.append(f"Medicine {med_num}: Cannot parse dose '{medicine.dose}'")
            return errors
        
        dose_mg = float(dose_match.group(1))
        
        if dose_mg < drug_info.min_dose_mg:
            errors.append(f"Medicine {med_num}: Dose {dose_mg}mg below minimum {drug_info.min_dose_mg}mg")
        elif dose_mg > drug_info.max_dose_mg:
            errors.append(f"Medicine {med_num}: Dose {dose_mg}mg exceeds maximum {drug_info.max_dose_mg}mg")
        
        return errors
    
    def _validate_frequency(self, medicine, drug_info: DrugInfo, med_num: int) -> List[str]:
        """Validate frequency is safe"""
        errors = []
        
        # Extract frequency
        freq_match = re.search(r'(\d+)\s*times?\s*(?:a\s*)?day', medicine.frequency, re.IGNORECASE)
        if not freq_match:
            return errors
        
        freq = int(freq_match.group(1))
        
        if freq < drug_info.freq_min:
            errors.append(f"Medicine {med_num}: Frequency {freq}x/day below recommended {drug_info.freq_min}x/day")
        elif freq > drug_info.freq_max:
            errors.append(f"Medicine {med_num}: Frequency {freq}x/day exceeds maximum {drug_info.freq_max}x/day")
        
        return errors
    
    def _check_allergy_conflict(self, drug_name: str, allergies: List[str]) -> bool:
        """Check if patient is allergic"""
        for allergy in allergies:
            if drug_name in allergy.lower() or allergy.lower() in drug_name:
                return True
        return False
    
    def _has_contraindications(self, drug_name: str, patient_age: Optional[int]) -> bool:
        """Check for contraindications"""
        drug_info = self._get_drug_info(drug_name)
        if not drug_info:
            return False
        
        if patient_age and (patient_age < drug_info.age_min or patient_age > drug_info.age_max):
            return True
        
        return False
    
    def _check_interactions(self, medicines: List) -> List[str]:
        """Check for dangerous drug-drug interactions"""
        warnings = []
        
        if len(medicines) < 2:
            return warnings
        
        med_names = [m.name.lower() for m in medicines]
        
        for i, med1 in enumerate(med_names):
            drug1 = self._get_drug_info(med1)
            if not drug1 or not drug1.interactions:
                continue
            
            for med2 in med_names[i+1:]:
                if med2 in drug1.interactions:
                    severity = drug1.interactions[med2]
                    if 'CRITICAL' in severity:
                        warnings.append(f"🚨 CRITICAL: {med1} + {med2} → {severity}")
                    else:
                        warnings.append(f"⚠️  {med1} + {med2} → {severity}")
        
        return warnings


# Test function
if __name__ == "__main__":
    from dataclasses import dataclass
    
    @dataclass
    class Medicine:
        name: str
        dose: str
        frequency: str
        duration: str
        instruction: str = ""
    
    validator = EnhancedValidationLayer()
    
    meds = [
        Medicine("Ibuprofen", "400 mg", "2 times a day", "5 days"),
        Medicine("Aspirin", "500 mg", "1 time a day", "7 days"),
    ]
    
    is_valid, errors, warnings = validator.validate_prescription(
        patient_age=45,
        medicines=meds,
        allergies=[]
    )
    
    print(f"Valid: {is_valid}")
    print(f"Errors: {errors}")
    print(f"Warnings: {warnings}")
