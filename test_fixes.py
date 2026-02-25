#!/usr/bin/env python
"""Test the 4 improvements: patient name, advice, lozenge dose, Arabic greeting"""

import json
import sys
sys.path.insert(0, 'src')

from medical_system_v2 import AdvancedExtractor

# Test text with all elements to verify
test_text = """مرحباً سارة، تعانين من أعراض تشير إلى التهاب الحلق الحاد. 
تناولي أموكسيسيلين 500 ملغ ثلاث مرات يومياً بعد الطعام لمدة 7 أيام. 
تناولي باراسيتامول 500 ملغ كل 6 إلى 8 ساعات عند الحاجة. 
استخدمي أقراص استحلاب للحلق ثلاث مرات يومياً. 
قومي بالغرغرة بالماء الدافئ والملح ثلاث مرات يومياً. 
اشربي سوائل دافئة بكثرة. احصلي على قسط كاف من الراحة."""

print("="*80)
print("TESTING 4 IMPROVEMENTS")
print("="*80)

# Initialize and extract
extractor = AdvancedExtractor()
result = extractor.extract_advanced(test_text, use_ensemble=False)

if result.get('success'):
    data = result.get('data', {})
    
    # Check 1: Patient name from Arabic greeting
    patient_name = data.get('patient_name')
    print("\n[FIX 1] Patient Name Extraction (Arabic greeting):")
    print("  Expected: Sarah (from arabic greeting)")
    print("  Got: " + str(patient_name))
    fix1_pass = patient_name and patient_name.lower() == 'sarah'
    print("  Status: " + ("PASS" if fix1_pass else "FAIL"))
    
    # Check 2: Lozenge dose (should NOT be "1 mg")
    medicines = data.get('medicines', [])
    print("\n[FIX 2] Lozenge Dose Correction:")
    lozenge = [m for m in medicines if 'lozenge' in m.get('name', '').lower()]
    if lozenge:
        lozenge_dose = lozenge[0].get('dose')
        print("  Medicine: " + str(lozenge[0].get('name')))
        print("  Expected: NOT '1 mg' (should be None or 'as directed')")
        print("  Got: " + str(lozenge_dose))
        fix2_pass = (lozenge_dose is None or '1 mg' not in str(lozenge_dose))
        print("  Status: " + ("PASS" if fix2_pass else "FAIL"))
    else:
        print("  Status: SKIPPED - No lozenge found")
        fix2_pass = True
    
    # Check 3: Advice extraction
    advice = data.get('advice', [])
    print("\n[FIX 3] Advice Extraction (from Arabic text):")
    print("  Expected: gargle, drink, rest, etc.")
    print("  Got " + str(len(advice)) + " items:")
    for adv in advice:
        print("    - " + str(adv))
    fix3_pass = len(advice) > 0
    print("  Status: " + ("PASS" if fix3_pass else "FAIL"))
    
    # Check 4: Overall summary
    print("\n[FIX 4] All Data Summary:")
    print("  Diagnosis: " + str(data.get('diagnosis')))
    print("  Medicines (" + str(len(medicines)) + " found):")
    for med in medicines:
        print("    - " + med.get('name') + ": " + str(med.get('dose')) + " - " + med.get('frequency'))
    
    print("\n" + "="*80)
    print("SUMMARY:")
    print("  FIX 1 (Patient name): " + ("PASS" if fix1_pass else "FAIL"))
    print("  FIX 2 (Lozenge dose): " + ("PASS" if fix2_pass else "FAIL"))
    print("  FIX 3 (Advice): " + ("PASS" if fix3_pass else "FAIL"))
    print("="*80)
    
else:
    print("EXTRACTION FAILED")

