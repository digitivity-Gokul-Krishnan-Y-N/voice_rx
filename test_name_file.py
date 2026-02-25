#!/usr/bin/env python
"""Quick test of _extract_patient_name function - output to file"""

import sys
import logging
sys.path.insert(0, 'src')

# Suppress logging to avoid encoding issues
logging.disable(logging.CRITICAL)

from medical_system_v2 import AdvancedExtractor

test_text = "مرحباً سارة، تعانين من أعراض"

extractor = AdvancedExtractor()
name = extractor._extract_patient_name(test_text)

with open('name_test_result.txt', 'w', encoding='utf-8') as f:
    f.write("Test input: Marhaba Sara with Arabic greeting\n")
    f.write("Function output: " + str(name) + "\n")
    f.write("Output repr: " + repr(name) + "\n")
    f.write("Is ASCII: " + str(all(ord(c) < 128 for c in (name or ""))) + "\n")

print("Result written to name_test_result.txt")
