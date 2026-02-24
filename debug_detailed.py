#!/usr/bin/env python3
"""Debug _correct_drug_name with detailed logging"""
import sys
import re
sys.path.insert(0, 'd:/voice_rx')

from src.medicine_database import KNOWN_DRUGS, DRUG_CORRECTIONS

# Simulate the actual function with logging
def debug_correct_drug_name(name: str) -> str:
    """Debug version with detailed logging"""
    original_name = name.lower().strip()
    corrected = original_name
    
    print(f"\n{'='*60}")
    print(f"Input: '{original_name}'")
    print(f"Step 0 - Start: corrected = '{corrected}'")
    
    # IMPROVEMENT 2: Arabic medicine name corrections
    arabic_medical_corrections = {
        r'\bسترات\s+البوتاسيوم\b|\blopassium\b|\blopa\s+potassium\b': 'potassium citrate',
        r'\bالبوتاسيوم\b|\blopassium\b': 'potassium',
        r'\bبروبيوتيك\b|\bciprobiotic\b': 'probiotic',
        r'\bفيتامين\s+سي\b|\bvitamin\s+see\b': 'vitamin c',
    }
    
    print(f"\nStep 1 - Arabic medicine corrections:")
    for pattern, replacement in arabic_medical_corrections.items():
        if re.search(pattern, corrected, flags=re.IGNORECASE):
            print(f"  Pattern '{pattern[:30]}...' MATCHED")
            corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)
            print(f"  → corrected = '{corrected}'")
        else:
            print(f"  Pattern '{pattern[:30]}...' no match")
    
    # Remove delivery formats
    delivery_formats = [
        r'\s+(?:oral\s+)?paste\s*$',
        r'\s+oral\s+solution\s*$',
        r'\s+tablets?\s*$',
        r'\s+capsules?\s*$',
    ]
    
    print(f"\nStep 2 - Remove delivery formats:")
    for pattern in delivery_formats:
        if re.search(pattern, corrected, flags=re.IGNORECASE):
            print(f"  Pattern '{pattern}' MATCHED")
            corrected = re.sub(pattern, '', corrected, flags=re.IGNORECASE)
            print(f"  → corrected = '{corrected}'")
    
    # Check if in KNOWN_DRUGS
    print(f"\nStep 3 - Check KNOWN_DRUGS:")
    if corrected in KNOWN_DRUGS:
        print(f"  ✅ '{corrected}' IS in KNOWN_DRUGS")
    else:
        print(f"  ❌ '{corrected}' is NOT in KNOWN_DRUGS")
    
    # Check if original input is in KNOWN_DRUGS
    print(f"\nStep 4 - Original input check:")
    if original_name in KNOWN_DRUGS:
        print(f"  ✅ '{original_name}' IS in KNOWN_DRUGS (func would return early?)")
    else:
        print(f"  ❌ '{original_name}' is NOT in KNOWNDRUGS")
    
    return corrected.lower()

# Test
test_cases = [
    "lopassium tablet",
    "ciprobiotic",
    "vitamin see",
]

for drug_name in test_cases:
    result = debug_correct_drug_name(drug_name)
    print(f"FINAL OUTPUT: '{result}'")
