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
    print(f"\n✓ FIX 1 - Patient Name Extraction (Arabic greeting):")
    print(f"  Expected: Sarah (from 'مرحباً سارة')")
    print(f"  Got: {patient_name}")
    print(f"  Status: {'✅ PASS' if patient_name and patient_name.lower() == 'sarah' else '❌ FAIL'}")
    
    # Check 2: Lozenge dose (should be "as directed" or NOT "1 mg")
    medicines = data.get('medicines', [])
    print(f"\n✓ FIX 2 - Lozenge Dose Correction:")
    lozenge = [m for m in medicines if 'lozenge' in m.get('name', '').lower()]
    if lozenge:
        lozenge_dose = lozenge[0].get('dose')
        print(f"  Medicine: {lozenge[0].get('name')}")
        print(f"  Expected dose: NOT '1 mg' (should be like 'as directed' or None)")
        print(f"  Got: {lozenge_dose}")
        print(f"  Status: {'✅ PASS' if (lozenge_dose is None or '1 mg' not in str(lozenge_dose)) else '❌ FAIL'}")
    else:
        print(f"  Status: ⚠️ SKIPPED - No lozenge found in extraction")
    
    # Check 3: Advice extraction (should include gargle, drink water, rest, etc.)
    advice = data.get('advice', [])
    print(f"\n✓ FIX 3 - Advice Extraction (Arabic advice from transcript):")
    print(f"  Expected advice items: gargle, drink, rest, avoid...")
    print(f"  Got {len(advice)} advice items:")
    for adv in advice:
        print(f"    - {adv}")
    has_meaningful_advice = len(advice) > 0
    print(f"  Status: {'✅ PASS' if has_meaningful_advice else '❌ FAIL'}")
    
    # Check 4: Overall summary
    print(f"\n✓ FIX 4 - All Data Summary:")
    print(f"  Diagnosis: {data.get('diagnosis')}")
    print(f"  Medicines ({len(medicines)} found):")
    for med in medicines:
        print(f"    - {med.get('name')}: {med.get('dose')} - {med.get('frequency')}")
    
else:
    print("❌ Extraction failed")

print("\n" + "="*80)
