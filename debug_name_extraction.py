#!/usr/bin/env python
"""Debug patient name extraction"""

import re
import sys
sys.path.insert(0, 'src')

test_text = "مرحباً سارة، تعانين من أعراض"

# Test the regex patterns
patterns = [
    (r'مرحبا[ً]?\s+([A-Za-z]+)', 'English name after Arabic greeting'),
    (r'مرحبا[ً]?\s+([\u0600-\u06FF]+)', 'Arabic name after greeting'),
]

print("Testing regex patterns on text: " + test_text)
print()

for pattern, desc in patterns:
    print("Pattern: " + pattern)
    print("Description: " + desc)
    match = re.search(pattern, test_text)
    if match:
        name = match.group(1)
        print("  MATCH: " + name)
        print("  Name mappings check:")
        name_mappings = {
            'سارة': 'Sarah',
            'محمد': 'Muhammad',
        }
        if name in name_mappings:
            print("    Found in mappings: " + name_mappings[name])
        else:
            print("    NOT in mappings")
    else:
        print("  NO MATCH")
    print()

# Now test the extraction function
from medical_system_v2 import AdvancedExtractor

extractor = AdvancedExtractor()
extracted_name = extractor._extract_patient_name(test_text)
print("Extracted name from function: " + str(extracted_name))
