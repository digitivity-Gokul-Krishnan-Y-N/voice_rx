#!/usr/bin/env python3
"""Check if corrected drug names are in KNOWN_DRUGS"""
import sys
sys.path.insert(0, 'd:/voice_rx')

from src.medicine_database import KNOWN_DRUGS

test_drugs = [
    "nitrofurantoin",
    "potassium citrate",
    "probiotic",
    "vitamin c",
    "stayhappi nitrofurantoin tablet",
]

for drug in test_drugs:
    is_in = drug.lower() in KNOWN_DRUGS
    print(f"'{drug:40}' in KNOWN_DRUGS: {is_in}")
