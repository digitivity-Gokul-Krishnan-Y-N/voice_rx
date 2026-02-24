#!/usr/bin/env python3
"""Debug _extract_advice behavior"""
import sys
sys.path.insert(0, 'd:/voice_rx')

from src.extraction import GroqLLMExtractor

print("=" * 70)
print("DEBUG: _extract_advice() - Understanding why it returns 0 items")
print("=" * 70)

extractor = GroqLLMExtractor()

# Test IMPROVEMENT 4 cases
test_cases = [
    "اشربي الكثير من الماء",
    "تجنبي المشروبات الساخة",
]

for transcript in test_cases:
    print(f"\nInput: '{transcript}'")
    result = extractor._extract_advice(transcript)
    print(f"Result: {result}")
    print(f"Number of items: {len(result)}")

# Let's also test English advice to see if that works
print("\n" + "=" * 70)
print("Testing English advice patterns:")
print("=" * 70)

english_test_cases = [
    "drink water regularly",
    "avoid triggers",
    "get rest",
]

for transcript in english_test_cases:
    print(f"\nInput: '{transcript}'")
    result = extractor._extract_advice(transcript)
    print(f"Result: {result}")
    print(f"Number of items: {len(result)}")
