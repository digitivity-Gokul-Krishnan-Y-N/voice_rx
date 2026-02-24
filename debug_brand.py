#!/usr/bin/env python3
"""Debug IMPROVEMENT 5 - Brand/Generic issues"""
import sys
sys.path.insert(0, 'd:/voice_rx')

from src.extraction import GroqLLMExtractor

extractor = GroqLLMExtractor()

print("=" * 70)
print("IMPROVEMENT 5: Brand/Generic Normalization - Debug")
print("=" * 70)

test_cases = [
    "stayhappi nitrofurantoin tablet",
    "stay happi",
    "uristat",
    "generic medicine",
]

for drug_name in test_cases:
    result = extractor._correct_drug_name(drug_name)
    print(f"\nInput:  '{drug_name}'")
    print(f"Output: '{result}'")
    print(f"Type: {type(result)}, Length: {len(result)}")
