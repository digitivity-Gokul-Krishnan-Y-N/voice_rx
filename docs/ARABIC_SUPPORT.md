# Arabic Language Support - Medical Extraction System

## Overview

The Voice RX medical extraction system has been enhanced to support **Arabic** language consultations alongside English, Tamil, and Thanglish (Tamil-English mix).

**Status**: ✅ **FULLY INTEGRATED**
- Whisper transcription detects Arabic (`ar` language code)
- LLM extraction prompt includes Arabic medical terminology
- Rule-based extraction supports Arabic patterns
- Language detection merged Arabic support

---

## 📍 Supported Languages

| Language | Code | Input Type | Example |
|----------|------|-----------|---------|
| **English** | `en` | Pure English | "Patient has fever and throat pain" |
| **Tamil** | `ta` | Tamil Unicode script | "நோயாளிக்கு காய்ச்சல் உள்ளது" |
| **Thanglish** | `tanglish` | Tamil words in English letters | "Patient ku kaichel irukku" |
| **Arabic** | `ar` | Arabic script or transliterated | "المريض لديه حمى وألم في الحلق" |

---

## 🔤 Arabic Medical Terminology

### Common Arabic Medical Terms (with transliteration)

**Diseases & Conditions**:
- `التهاب الحلق` (iltiab alhalq) = **Pharyngitis / Throat inflammation**
- `عدوى بكتيرية` (adwa bakteriya) = **Bacterial infection**
- `عدوى فيروسية` (adwa virusia) = **Viral infection**
- `الالتهاب الرئوي` (iltiab alri'awi) = **Pneumonia**
- `السعال` (suaal) = **Cough**
- `الإسهال` (ishal) = **Diarrhea**
- `الحمى` (humma) = **Fever**
- `الصداع` (sudaa) = **Headache**
- `ضغط الدم` (daghtt alddam) = **Hypertension**
- `السكري` (sakkari) = **Diabetes**

**Medicines** (transliterated):
- `أسبرين` (aspireen) = **Aspirin**
- `الباراسيتامول` (paracetamol) = **Paracetamol**
- `الأموكسيسيللين` (amoxicillin) = **Amoxicillin**
- `الأزيثرومايسين` (azithromycin) = **Azithromycin**
- `السيبروفلوكساسين` (ciprofloxacin) = **Ciprofloxacin**
- `اللوراتادين` (loratadine) = **Loratadine**
- `ليفوسيتيريزين` (levocetirizine) = **Levocetirizine**

**Frequencies & Dosages**:
- `مرات في اليوم` (marat fi alyawm) = **Times per day**
- `ثلاث مرات` (talat marat) = **3 times**
- `مرة واحدة` (marra wahida) = **Once**
- `ملغ` / `mg` (milligram) = **Milligram**
- `أيام` (ayyam) = **Days**
- `أسبوع` (usbua) = **Week**

**Instructions**:
- `بعد الأكل` (baada alakl) = **After meals**
- `قبل النوم` (qabl alnawm) = **Before sleep**
- `كل` (kull) = **Every**
- `في الصباح` (fi assabah) = **In the morning**
- `في المساء` (fi almasa) = **In the evening**

---

## 🔧 Implementation Details

### 1. **Language Detection Enhancement**

The system now recognizes Arabic at multiple levels:

```python
# In medical_system_v2.py:
# Whisper detects 'ar' language code during transcription
# If audio_detected_lang == "ar", lang_code is set to "ar"
# Language confidence: 0.95 (high confidence from Whisper)
```

### 2. **Improved Extraction Prompt** 

The Groq LLM extraction prompt now includes:

```
📍 ARABIC CONSULTATION:
- 'مرض'/'marad' = disease
- 'دواء'/'dawa' = medicine
- 'ألم'/'alam' = pain
- 'حمى'/'humma' = fever
- 'صداع'/'sudaa' = headache
- Frequency: 'مرات في اليوم'/'marat fi alyawm' = times a day
- Instructions: 'بعد الأكل'/'baada alakl' = after food
```

### 3. **Arabic Medicine/Diagnosis Extraction**

Added Arabic-specific regex patterns in `_extract_medicines_advanced()` and `_extract_diagnosis_advanced()`:

```python
# Islamic diagnosis patterns
(r'iltiab\s+alhalq|التهاب الحلق', 'pharyngitis', 1),
(r'adwa\s+bakteriya|عدوى بكتيرية', 'bacterial infection', 1),

# Arabic complaint patterns
(r'sudaa|صداع', 'headache', 2),
(r'humma|حمى', 'fever', 2),
(r'suaal|سعال', 'cough', 2),
```

### 4. **Arabic Transcription Error Correction**

Added common Arabic transcription error corrections in `_correct_medical_terms()`:

```python
arabic_corrections = {
    r'\baspireen\b': 'aspirin',
    r'\bdawaa\b|\bdiwa\b': 'medicine',
    r'\bmarad\b': 'disease',
    r'\balam\b': 'pain',
    r'\bhumma\b': 'fever',
    ...
}
```

### 5. **Medicine Database Enhancement**

Updated `medicine_database.py` to include Arabic transliterated medicine names:

```python
'aspireen', 'paracetal', 'amoxysilan', 'azithro', 'ciprofloxacine',
'levoceti', 'omeprazol', 'domeperidone'
```

---

## 📊 System Flow for Arabic Input

```
┌─────────────────────────────────────┐
│  ARABIC AUDIO INPUT                 │
│  (Medical consultation in Arabic)   │
└──────────────┬──────────────────────┘
               ↓
      ┌────────────────────┐
      │ Whisper Transcription
      │ • Detects lang='ar'
      │ • Outputs Arabic text
      └────────────┬───────┘
                   ↓
      ┌────────────────────────────┐
      │ Language Detection
      │ • Audio-level: ar (0.95)   
      │ • Merged confidence: ar    │
      └────────────┬───────────────┘
                   ↓
      ┌────────────────────────────┐
      │ Arabic Normalization      │
      │ • Corrects transliterations│
      │ • Maps to English terms    │
      └────────────┬───────────────┘
                   ↓
      ┌────────────────────────────┐
      │ Extraction (Groq LLM)      │
      │ • Includes Arabic          │
      │   terminology in prompt    │
      │ • Returns English JSON     │
      └────────────┬───────────────┘
                   ↓
      ┌────────────────────────────┐
      │ JSON Output (English)      │
      │ {                          │
      │   "patient_name": "Ahmed", │
      │   "diagnosis": ["fever"],  │
      │   "medicines": [ ... ]     │
      │ }                          │
      └────────────────────────────┘
```

---

## 🧪 Testing Arabic Support

### Test Case 1: Arabic Pharyngitis Consultation

**Input (Arabic)**:
```
"المريض أحمد عمره 35 سنة. يشتكي من الم في الحلق وحمى 
 التشخيص التهاب حلق بكتيري. وصفت له أموكسيسيللين 500 ملغ ثلاث مرات في اليوم 
 لمدة 5 أيام"
```

**Expected Output (English JSON)**:
```json
{
  "patient_name": "Ahmed",
  "age": "35",
  "complaints": ["throat pain", "fever"],
  "diagnosis": ["bacterial pharyngitis"],
  "medicines": [
    {
      "name": "amoxicillin",
      "dose": "500 mg",
      "frequency": "3 times a day",
      "duration": "5 days",
      "instruction": ""
    }
  ],
  "tests": [],
  "advice": ["complete full course"]
}
```

### Test Case 2: Mixed Arabic-English Consultation

**Input**:
```
"Patient Fatima has humma and headache. Diagnosis acute pharyngitis. 
 وصفت لها Paracetamol 500 mg مرتين في اليوم"
```

**System Behavior**:
- Whisper detects mixed `ar` + `en`
- System identifies as Arabic-dominant
- Extracts mixed content correctly

---

## ✨ Key Features

| Feature | Status | Details |
|---------|--------|---------|
| **Audio Transcription** | ✅ | Whisper supports Arabic |
| **Language Detection** | ✅ | Recognizes `ar` code |
| **LLM Extraction** | ✅ | Groq prompt includes Arabic context |
| **Rule-Based Fallback** | ✅ | Arabic regex patterns added |
| **Medicine Recognition** | ✅ | Arabic transliterations supported |
| **Diagnosis Extraction** | ✅ | Arabic medical terms mapped to English |
| **Error Correction** | ✅ | Arabic transcription errors handled |
| **Database Support** | ✅ | Arabic drug names indexed |

---

## 📝 Example Use Cases

### Use Case 1: Gulf Healthcare Provider
- Doctor conducts consultation in Arabic
- Voice RX transcribes and extracts prescription
- Output: Standardized English JSON for medical record system

### Use Case 2: Multilingual Clinic
- Patients may speak Arabic, English, or Tamil
- Single system handles all languages
- Consistent JSON output for integration

### Use Case 3: Medical Research
- Collect clinical data across Arabic-speaking regions
- Extract prescription patterns
- Analyze medication usage (standardized English terms)

---

## 🔍 Supported Arabic Dialects

**Modern Standard Arabic (MSA)** is primarily supported. **Regional dialects** (Egyptian, Levantine, Gulf, Moroccan) may have ASR challenges due to Whisper's MSA bias, but system includes transliteration fallbacks for common terms.

---

## 🚀 Future Enhancements

- [ ] Add support for Arabic numerals (١٢٣) detection
- [ ] Expand medicine database with regional brand names (Tylenol → Panadol)
- [ ] Add Arabic-specific abbreviations (CBC → تحليل الدم)
- [ ] Fine-tune prompts for regional Arabic variants
- [ ] Add validation rules for Arabic prescription formats

---

## 📚 References

**Whisper Language Support**: https://github.com/openai/whisper/blob/main/whisper/tokenizer.py
**ISO 639-1 Code**: `ar` = Arabic

---

**Version**: 1.0 (February 2026)
**Last Updated**: 2026-02-24
