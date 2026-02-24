#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test Arabic extraction with real medical consultation"""

import sys
import json
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from medical_system_v2 import AdvancedExtractor

# Arabic medical consultation
arabic_text = """مرحباً ميرا،

تعانين من أعراض تشير إلى التهاب المعدة الحاد، وهو التهاب في بطانة المعدة. قد يحدث بسبب العدوى، أو تناول الطعام بشكل غير منتظم، أو التوتر، أو تناول الأطعمة الحارة والدهنية بكثرة. الهدف من العلاج هو تقليل تهيج المعدة وتخفيف الأعراض ومساعدة المعدة على الشفاء.

تناولي بانتوبرازول 40 ملغ مرة واحدة يومياً قبل الإفطار لتقليل حمض المعدة.
تناولي شراب مضاد للحموضة 10 مل بعد الأكل مرتين يومياً لتخفيف الأعراض.
يمكنك تناول أوندانسيترون 4 ملغ عند الحاجة إذا كان هناك غثيان أو قيء (حسب الجرعة الموصوفة).
تناولي معلق سوكرالفات قبل الوجبات لحماية بطانة المعدة.
تناولي كبسولة بروبيوتيك مرة واحدة يومياً بعد الطعام لدعم الهضم.

احرصي على تناول وجبات صغيرة ومتكررة ولا تهملي الطعام. تجنبي الأطعمة الحارة والدهنية والمقلية والحمضية. قللي من القهوة والشاي والمشروبات الغازية. اشربي كمية كافية من الماء، وتجنبي تناول الطعام في وقت متأخر من الليل. حاولي تقليل التوتر واحصلي على قسط كافٍ من الراحة.

قد تظهر آثار جانبية خفيفة مثل الانتفاخ أو الإمساك أو الصداع. إذا شعرتِ بألم شديد في البطن، أو قيء مستمر، أو دم في القيء أو البراز، أو براز أسود اللون، يجب طلب المساعدة الطبية فوراً.

إذا لم تتحسن الأعراض خلال عدة أيام أو ساءت في أي وقت، راجعي الطبيب.
نتمنى لك الشفاء العاجل"""

print("=" * 80)
print("🌍 ARABIC EXTRACTION TEST - Medical Consultation")
print("=" * 80)
print(f"\n📝 Input Language: ARABIC")
print(f"📊 Input Length: {len(arabic_text)} characters")
print(f"\n🔍 Testing extraction from Arabic medical consultation...")
print("-" * 80)

extractor = AdvancedExtractor()
result = extractor.extract_advanced(transcript=arabic_text, use_ensemble=False)

print("\n✅ Extraction Result:")
print("-" * 80)
print(json.dumps(result, indent=2, ensure_ascii=False))

print("\n" + "=" * 80)
print("📊 EXTRACTED DATA SUMMARY:")
print("=" * 80)

if result['success']:
    data = result['data']
    print(f"\n👤 Patient Name: {data.get('patient_name', 'N/A')}")
    print(f"🏥 Diagnosis: {', '.join(data.get('diagnosis', []))}")
    print(f"💊 Medicines: {len(data.get('medicines', []))} items")
    for med in data.get('medicines', []):
        print(f"   - {med.get('name', 'N/A')}: {med.get('dose', 'N/A')} x {med.get('frequency', 'N/A')}")
    print(f"🩺 Complaints: {', '.join(data.get('complaints', []))}")
    print(f"💭 Advice: {len(data.get('advice', []))} recommendations")
    print(f"\n✨ Method Used: {result.get('method', 'unknown')}")
else:
    print("❌ Extraction Failed!")
