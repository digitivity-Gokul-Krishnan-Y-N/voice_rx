#!/usr/bin/env python
"""Quick test of _extract_patient_name function"""

import sys
sys.path.insert(0, 'src')

from medical_system_v2 import AdvancedExtractor

test_text = """مرحباً سارة، تعانين من أعراض تشير إلى التهاب الحلق الحاد. 
تناولي أموكسيسيلين 500 ملغ ثلاث مرات يومياً بعد الطعام لمدة 7 أيام."""

extractor = AdvancedExtractor()
name = extractor._extract_patient_name(test_text)

print("Input text snippet: Marhaba Sara [Arabic], symptoms of sore throat...")
print("Function output: " + str(name))
print("Type: " + str(type(name)))
print("Is ASCII: " + str(all(ord(c) < 128 for c in (name or ""))))
