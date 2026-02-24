#!/usr/bin/env python3
"""Trace through _correct_drug_name with detailed steps"""
import sys
import re
sys.path.insert(0, 'd:/voice_rx')

from difflib import get_close_matches, SequenceMatcher
from src.medicine_database import KNOWN_DRUGS

def trace_correction(name: str):
    """Trace through the correction steps"""
    print(f"\n{'='*70}")
    print(f"Input: '{name}'")
    print(f"{'='*70}")
    
    original_name = name.lower().strip()
    corrected = original_name
    
    print(f"1. Start: corrected = '{corrected}'")
    
    # IMPROVEMENT 5: Brand/generic (now applied BEFORE fuzzy matching)
    print(f"\n2. Brand/generic normalization:")
    brand_generic_map = {
        r'\bstayhappi\b': 'nitrofurantoin',
        r'\bstay\s*happi\b': 'nitrofurantoin',
        r'\buristat\b': 'nitrofurantoin',
    }
    
    for pattern, generic_name in brand_generic_map.items():
        if re.search(pattern, corrected, flags=re.IGNORECASE):
            print(f"  Pattern '{pattern}' matched!")
            corrected = re.sub(pattern, generic_name, corrected, flags=re.IGNORECASE)
            print(f"  → corrected = '{corrected}'")
            break
    else:
        print(f"  No pattern matched")
    
    # Fuzzy matching
    print(f"\n3. Fuzzy matching:")
    corrected_lower = corrected.lower().strip()
    print(f"  corrected_lower = '{corrected_lower}'")
    print(f"  In KNOWN_DRUGS: {corrected_lower in KNOWN_DRUGS}")
    
    if corrected_lower and corrected_lower not in KNOWN_DRUGS:
        print(f"  Not in KNOWN_DRUGS, trying fuzzy match...")
        for cutoff in [0.75, 0.65, 0.55, 0.45]:
            matches = get_close_matches(corrected_lower, KNOWN_DRUGS, n=1, cutoff=cutoff)
            if matches:
                fuzzy_match = matches[0].lower()
                print(f"    Cutoff {cutoff}: Found '{fuzzy_match}'")
                fuzzy_similarity = SequenceMatcher(None, original_name, fuzzy_match).ratio()
                print(f"    Similarity to original: {fuzzy_similarity:.2f}")
                if fuzzy_similarity > 0.7:
                    print(f"    Too similar to original, skipping")
                    break
                print(f"    Would return: {fuzzy_match}")
                corrected = fuzzy_match
                break
    
    print(f"\n4. Final result: '{corrected}'")
    return corrected

# Test
test_cases = [
    "stay happi",
    "generic medicine",
]

for test in test_cases:
    trace_correction(test)
