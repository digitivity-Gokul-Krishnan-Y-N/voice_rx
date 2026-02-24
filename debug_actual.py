#!/usr/bin/env python3
"""Test actual _correct_drug_name from extraction.py"""
import sys
sys.path.insert(0, 'd:/voice_rx')

from src.extraction import GroqLLMExtractor
from difflib import get_close_matches
from src.medicine_database import KNOWN_DRUGS
import re

extractor = GroqLLMExtractor()

print("Testing actual _correct_drug_name():")
print("=" * 70)

test_input = "lopassium tablet"
result = extractor._correct_drug_name(test_input)

print(f"\nInput: '{test_input}'")
print(f"Result: '{result}'")
print(f"Result in KNOWN_DRUGS: {result in KNOWN_DRUGS}")
print(f"Input in KNOWN_DRUGS: {test_input in KNOWN_DRUGS}")
print(f"Input.lower() in KNOWN_DRUGS: {test_input.lower() in KNOWN_DRUGS}")

# Let's manually trace through what SHOULD happen
print("\n" + "=" * 70)
print("Manual trace:")
print("=" * 70)

original_name = test_input.lower().strip()
corrected = original_name
print(f"1. Start: corrected = '{corrected}'")

# Arabic corrections
arabic_medical_corrections = {
    r'\bسترات\s+البوتاسيوم\b|\blopassium\b|\blopa\s+potassium\b': 'potassium citrate',
}

for pattern, replacement in arabic_medical_corrections.items():
    if re.search(pattern, corrected, flags=re.IGNORECASE):
        corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)
        print(f"2. Arabic correction matched: corrected = '{corrected}'")
        break

# Delivery formats
delivery_pattern = r'\s+tablets?\s*$'
if re.search(delivery_pattern, corrected, flags=re.IGNORECASE):
    corrected = re.sub(delivery_pattern, '', corrected, flags=re.IGNORECASE)
    print(f"3. After delivery format removal: corrected = '{corrected}'")

# Check KNOWN_DRUGS
corrected_lower = corrected.lower().strip()
print(f"4. corrected_lower = '{corrected_lower}'")
print(f"   In KNOWN_DRUGS: {corrected_lower in KNOWN_DRUGS}")

if not (corrected_lower in KNOWN_DRUGS):
    print("5. Not in KNOWN_DRUGS, trying fuzzy match...")
    for cutoff in [0.75, 0.65, 0.55, 0.45]:
        matches = get_close_matches(corrected_lower, KNOWN_DRUGS, n=1, cutoff=cutoff)
        if matches:
            print(f"   Cutoff {cutoff}: Found '{matches[0]}'")
            print(f"   Would return: {matches[0].lower()}")
            break
else:
    print(f"5. In KNOWN_DRUGS! Would continue to next steps and return {corrected}")
