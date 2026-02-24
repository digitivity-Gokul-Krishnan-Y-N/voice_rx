#!/usr/bin/env python3
"""Debug actual _correct_drug_name execution"""
import sys
sys.path.insert(0, 'd:/voice_rx')

from src.extraction import GroqLLMExtractor
from src.medicine_database import KNOWN_DRUGS

print("=" * 70)
print("DEBUG: _correct_drug_name() execution trace")
print("=" * 70)

extractor = GroqLLMExtractor()

test_cases = [
    "lopassium tablet",
    "ciprobiotic", 
    "vitamin see",
]

for drug_name in test_cases:
    print(f"\nInput: '{drug_name}'")
    result = extractor._correct_drug_name(drug_name)
    print(f"Output: '{result}'")
    
    # Check if result is in KNOWN_DRUGS
    if result.lower() in KNOWN_DRUGS:
        print(f"✅ '{result}' is in KNOWN_DRUGS")
    else:
        print(f"❌ '{result}' is NOT in KNOWN_DRUGS")
        # Check if similar drugs are in KNOWN_DRUGS
        similar_drugs = [d for d in KNOWN_DRUGS if 'potassium' in d or 'probiotic' in d or 'vitamin' in d][:5]
        print(f"   Similar drugs in DB: {similar_drugs[:3]}")

print("\n" + "=" * 70)
print("DEBUG: _extract_advice() after database fix")
print("=" * 70)

test_cases_advice = [
    "اشربي الكثير من الماء",
    "تجنبي المشروبات الساخة",
]

for transcript in test_cases_advice:
    print(f"\nInput: '{transcript}'")
    result = extractor._extract_advice(transcript)
    print(f"Advice extracted: {result}")
    print(f"Number of items: {len(result)}")
