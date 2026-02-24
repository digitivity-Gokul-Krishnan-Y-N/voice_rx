#!/usr/bin/env python3
import re

# Test IMPROVEMENT 2 patterns
print("=" * 70)
print("DEBUG: IMPROVEMENT 2 - Pattern Matching Test")
print("=" * 70)

arabic_medical_corrections = {
    r'\bسترات\s+البوتاسيوم\b|\blopassium\b|\blopa\s+potassium\b': 'potassium citrate',
    r'\bالبوتاسيوم\b|\blopassium\b': 'potassium',
    r'\bبروبيوتيك\b|\bciprobiotic\b': 'probiotic',
    r'\bفيتامين\s+سي\b|\bvitamin\s+see\b': 'vitamin c',
}

test_cases = [
    ("lopassium tablet", "potassium citrate"),
    ("ciprobiotic", "probiotic"),
    ("vitamin see", "vitamin c"),
]

for input_text, expected in test_cases:
    print(f"\nInput: '{input_text}'")
    print(f"Expected: '{expected}'")
    
    corrected = input_text.lower().strip()
    original = corrected
    
    for pattern, replacement in arabic_medical_corrections.items():
        print(f"  Trying pattern: {pattern}")
        match = re.search(pattern, corrected, flags=re.IGNORECASE)
        if match:
            print(f"    ✅ MATCHED: {match.group()}")
            corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)
            print(f"    → After substitution: '{corrected}'")
        else:
            print(f"    ❌ No match")
    
    # Remove delivery formats
    delivery_formats = [
        r'\s+(?:oral\s+)?paste\s*$',
        r'\s+oral\s+solution\s*$',
        r'\s+tablets?\s*$',
        r'\s+capsules?\s*$',
    ]
    
    for pattern in delivery_formats:
        corrected = re.sub(pattern, '', corrected, flags=re.IGNORECASE)
    
    corrected = corrected.strip()
    print(f"After delivery format removal: '{corrected}'")
    print(f"Final Result: '{corrected}'")
    print(f"Match: {'✅' if expected.lower() in corrected.lower() else '❌'}")

print("\n" + "=" * 70)
print("DEBUG: IMPROVEMENT 4 - Arabic Advice Pattern Test")
print("=" * 70)

arabic_advice_patterns = [
    (r'اشربي', 'drink water regularly'),
    (r'تجنبي', 'avoid triggers'),
    (r'حافظي', 'maintain personal hygiene'),
    (r'لا تؤخري', 'do not delay treatment'),
]

advice_test_cases = [
    "اشربي الكثير من الماء",
    "تجنبي المشروبات الساخة",
    "حافظي على النظافة الشخصية",
]

for text in advice_test_cases:
    print(f"\nText: '{text}'")
    advice = []
    for ar_pattern, ar_advice_text in arabic_advice_patterns:
        print(f"  Trying pattern: {ar_pattern}")
        match = re.search(ar_pattern, text)
        if match:
            print(f"    ✅ MATCHED: {match.group()}")
            advice.append(ar_advice_text)
        else:
            print(f"    ❌ No match")
    
    print(f"Advice extracted: {len(advice)} items: {advice}")

print("\n" + "=" * 70)
print("DEBUG: IMPROVEMENT 5 - Brand/Generic Pattern Test")
print("=" * 70)

brand_generic_map = {
    r'\bstayhappi\b': 'nitrofurantoin',
    r'\bstay\s*happi\b': 'nitrofurantoin',
    r'\buristat\b': 'nitrofurantoin',
}

brand_test_cases = [
    "stayhappi",
    "stay happi",
    "uristat",
    "stayhappi nitrofurantoin tablet",
]

for input_text in brand_test_cases:
    print(f"\nInput: '{input_text}'")
    corrected = input_text.lower().strip()
    original = corrected
    
    for pattern, generic_name in brand_generic_map.items():
        print(f"  Trying pattern: {pattern}")
        match = re.search(pattern, corrected, flags=re.IGNORECASE)
        if match:
            print(f"    ✅ MATCHED: {match.group()}")
            corrected = re.sub(pattern, generic_name, corrected, flags=re.IGNORECASE)
            print(f"    → After substitution: '{corrected}'")
        else:
            print(f"    ❌ No match")
    
    print(f"Final Result: '{corrected}'")
