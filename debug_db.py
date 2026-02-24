#!/usr/bin/env python3
"""Debug MEDICINE_DB_AVAILABLE and ADVICE_MAPPING"""
import sys
sys.path.insert(0, 'd:/voice_rx')

try:
    from src.medicine_database import KNOWN_DRUGS, DRUG_CORRECTIONS, STANDARD_ADVICE, ADVICE_MAPPING
    print("✅ Successfully imported from medicine_database")
    print(f"KNOWN_DRUGS: {len(KNOWN_DRUGS)} items")
    print(f"STANDARD_ADVICE: {len(STANDARD_ADVICE)} items")
    print(f"STANDARD_ADVICE content: {STANDARD_ADVICE[:3]}")
    print(f"ADVICE_MAPPING: {ADVICE_MAPPING}")
    db_available = True
except Exception as e:
    print(f"❌ Failed to import: {e}")
    db_available = False

print(f"\nMEDICINE_DB_AVAILABLE should be: {db_available}")

# Now test the import in extraction.py
try:
    from src.extraction import GroqLLMExtractor
    from src import extraction
    print(f"\n✅ Successfully imported GroqLLMExtractor")
    print(f"extraction.MEDICINE_DB_AVAILABLE = {extraction.MEDICINE_DB_AVAILABLE}")
    print(f"extraction.ADVICE_MAPPING = {extraction.ADVICE_MAPPING if hasattr(extraction, 'ADVICE_MAPPING') else 'NOT AVAILABLE'}")
except Exception as e:
    print(f"❌ Failed to import: {e}")
