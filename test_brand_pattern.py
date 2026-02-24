#!/usr/bin/env python3
"""Test brand/generic pattern matching"""
import re

patterns = [
    r'\bstayhappi\b',
    r'\bstay\s*happi\b',
]

test_strings = [
    "stay happi",
    "stay  happi",
    "stayhappi",
]

for test_str in test_strings:
    print(f"\nTesting: '{test_str}'")
    for pattern in patterns:
        match = re.search(pattern, test_str, flags=re.IGNORECASE)
        if match:
            print(f"  ✅ Pattern '{pattern}' matched: '{match.group()}'")
        else:
            print(f"  ❌ Pattern '{pattern}' no match")
