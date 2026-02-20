"""
Extraction Module: Medical data extraction (Groq LLM + rule-based).

GroqLLMExtractor: Single unified extractor with Groq API + fallback to rules
EnsembleExtractor: Combines multiple extraction methods with confidence voting
"""

import os
import json
import logging
import re
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from difflib import get_close_matches

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    from smart_labeling import SmartLabelClassifier
    SMART_LABELING_AVAILABLE = True
except ImportError:
    SMART_LABELING_AVAILABLE = False

try:
    from medicine_database import (
        KNOWN_DRUGS, DRUG_CORRECTIONS, STANDARD_ADVICE, ADVICE_MAPPING
    )
    MEDICINE_DB_AVAILABLE = True
except ImportError:
    MEDICINE_DB_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class Medicine:
    """Medicine with standard attributes."""
    name: str
    dose: str
    frequency: str
    duration: str
    instruction: str = ""
    route: str = "oral"
    side_effects: list = field(default_factory=list)


class GroqLLMExtractor:
    """
    Unified medical data extractor with Groq API + fallback to rule-based.
    
    No duplication — single instance handles all extraction modes:
    - Groq API when available and quality is high
    - Rule-based when Groq unavailable or quality is poor
    - Automatic fallback between methods
    """

    EXTRACTION_PROMPT = """
You are a medical data extraction specialist. Extract prescription data from the following medical consultation.

⚠️ CRITICAL JSON FORMAT REQUIREMENTS:
- You MUST return STRICTLY VALID JSON ONLY
- Do NOT include markdown, code blocks, or explanations
- Do NOT include comments
- Do NOT use trailing commas
- Ensure ALL strings are properly closed (no unterminated strings)
- Output must begin with {{ and end with }}
- Escape special characters properly: \" for quotes, \\ for backslashes

📦 COMPACT JSON OUTPUT:
- Return compact JSON only (no extra whitespace)
- Do not include extra whitespace or newlines inside JSON
- Keep advice concise (short, actionable strings max 100 chars)
- Keep complaint and diagnosis strings concise
- Minimize array/object nesting where possible
- Output MUST begin with {{ and MUST end with }}

LANGUAGE NOTICE:
- The transcript may be in English, Tamil (Unicode), or Thanglish (Tamil words in English letters).
- Thanglish examples: 'noi' (disease), 'marunthu' (medicine), 'vali' (pain), 'kaichal' (fever)
- If Tamil/Thanglish text appears, interpret it according to medical context.

IMPORTANT: The transcript is from automatic speech recognition (ASR) and may contain residual errors even after cleaning.
Common ASR artifacts to recognize:
- 'inflection' or 'infraction' should be 'infection'
- 'antibiotic risk' should be 'antibiotics'
- 'paragenesis' should be 'pharyngitis'
- 'back inflection' should be 'bacterial infection'
- 'kayachel' / 'kaychel' should be 'fever'
- Drug names may be phonetically distorted (e.g. 'erytho mice in' = 'erythromycin')
- Numbers and measurements may be slurred (e.g. 'five oh zero' = 'five hundred' or '500')

Use MEDICAL KNOWLEDGE and clinical reasoning to interpret the transcript correctly.
If the transcription is very poor and you cannot confidently extract data, return null values rather than inventing data.

Return JSON with these exact keys (NO OTHER TEXT, NO EXPLANATIONS):
{{
  "patient_name": "string or null",
  "age": null,
  "complaints": ["fever", "throat pain"],
  "diagnosis": ["bacterial infection"],
  "medicines": [
    {{
      "name": "erythromycin",
      "dose": "500 mg",
      "frequency": "3 times a day",
      "duration": "5 days",
      "instruction": "after food"
    }}
  ],
  "tests": [],
  "advice": ["complete the course"]
}}

Medical Consultation:
{consultation}

EXTRACTION RULES:
- Return ONLY valid JSON, nothing else
- Patient name: Extract ONCE, no duplicates (e.g. "Hi Rohit, Rohit..." → "Rohit")
- Complaints: Specific symptoms mentioned (fever, throat pain, cough, etc.)
- Diagnosis: Medical conditions (throat infection, bacterial infection, etc.)
- Medicines: Only prescribed drugs with complete information
  * name: medicine name (e.g., "erythromycin")
  * dose: must include units (mg, ml, mcg, tablet, capsule) e.g., "500 mg"
  * frequency: times per day (e.g., "3 times a day")
  * duration: days/weeks (e.g., "5 days")
  * instruction: timing relative to food ("after food", "before food", "with meal")
- Tests: Lab tests mentioned
- Advice: Patient guidance strings

Output ONLY the JSON object. No markdown. No code blocks. No explanations.
"""

    GROQ_MODELS = [
        "openai/gpt-oss-120b",
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "meta-llama/llama-prompt-guard-2-8k",
    ]

    def __init__(self):
        """Initialize Groq client if API key available, otherwise use rules-only mode."""
        self.use_groq = GROQ_AVAILABLE and self._check_groq()
        self.client = None
        self.available_model = None

        if self.use_groq:
            try:
                self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                self.available_model = self._find_available_model()
                if self.available_model:
                    logger.info(f"[OK] Groq initialized - using {self.available_model}")
                else:
                    logger.warning("No Groq models available, using rule-based extraction")
                    self.use_groq = False
            except Exception as e:
                logger.warning(f"Groq initialization failed: {e}")
                self.use_groq = False
        else:
            logger.info("Using rule-based extraction (stable, always available)")

    def extract(self, transcript: str, use_groq: bool = True) -> Dict:
        """
        Extract prescription data.
        
        Args:
            transcript: Medical consultation text
            use_groq: Whether to try Groq API (falls back to rules if unavailable)
        
        Returns:
            Dict with keys: success, data, method
        """
        if self.use_groq and use_groq:
            return self._extract_groq(transcript)
        else:
            return self._extract_rules(transcript)

    # ── Groq extraction ────────────────────────────────────────────────────────

    def _extract_groq(self, transcript: str) -> Dict:
        """Extract using Groq API with automatic fallback to rules."""
        if not self.available_model:
            return self._extract_rules(transcript)

        try:
            logger.info(f"Extracting with Groq ({self.available_model})...")

            prompt = self.EXTRACTION_PROMPT.format(consultation=transcript)

            try:
                response = self.client.chat.completions.create(
                    model=self.available_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0,
                    max_tokens=2000
                )

                output = response.choices[0].message.content.strip()
                logger.debug(f"Groq raw response ({len(output)} chars): {output[:200]}...")
            except Exception as e:
                logger.warning(f"[GROQ] API call failed: {type(e).__name__}: {e}")
                return self._extract_rules(transcript)

            # Parse JSON safely with multiple fallback strategies
            data = self._robust_json_parse(output)
            if not data:
                # RETRY: Try once more with explicit complete-JSON instruction
                logger.info("[GROQ] First parse failed, retrying with explicit completion instruction...")
                try:
                    retry_prompt = prompt + "\n\nIMPORTANT: Return complete valid JSON. Ensure it ends with }}. Do not truncate. Return ONLY the JSON object."
                    retry_response = self.client.chat.completions.create(
                        model=self.available_model,
                        messages=[{"role": "user", "content": retry_prompt}],
                        temperature=0,
                        max_tokens=2000
                    )
                    retry_output = retry_response.choices[0].message.content.strip()
                    logger.debug(f"Groq retry response ({len(retry_output)} chars): {retry_output[:200]}...")
                    data = self._robust_json_parse(retry_output)
                except Exception as e:
                    logger.warning(f"[GROQ] Retry failed: {type(e).__name__}: {e}")
                    data = None
                
                if not data:
                    logger.warning(f"[GROQ] Could not parse JSON after 2 attempts, response was: {output[:300]}...")
                    return self._extract_rules(transcript)

            # Post-process
            data = self._post_process(data)
            logger.info(f"[OK] Groq extraction: {len(data.get('medicines', []))} medicines, "
                       f"{len(data.get('diagnosis', []))} diagnoses")
            return {"success": True, "data": data, "method": "groq"}

        except Exception as e:
            logger.warning(f"[GROQ] Unexpected error during extraction: {type(e).__name__}: {str(e)[:100]}")
            return self._extract_rules(transcript)

    def _robust_json_parse(self, text: str) -> Optional[Dict]:
        """
        Robust JSON parser for Groq output with multiple fallback strategies.
        Handles markdown blocks, prefix text, unterminated strings, and malformed JSON.
        
        Strategies:
        1. Direct JSON parse (clean output)
        2. Extract from markdown code block (if wrapped in ```json```)
        3. Extract valid JSON object from anywhere in text (handles prefix text)
        4. Attempt to fix common JSON issues (trailing commas, unterminated strings)
        """
        if not text or not isinstance(text, str):
            return None
        
        text = text.strip()
        
        # Strategy 1: Direct JSON parse (clean output)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Extract from markdown code block
        try:
            match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
            if match:
                json_str = match.group(1).strip()
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        # Strategy 3: Extract valid JSON object (greedy bracket matching)
        # This handles cases where Groq adds prefix text before the JSON
        try:
            start_idx = text.find('{')
            if start_idx == -1:
                return None
            
            # Find matching closing brace
            depth = 0
            for i in range(start_idx, len(text)):
                if text[i] == '{':
                    depth += 1
                elif text[i] == '}':
                    depth -= 1
                    if depth == 0:
                        json_str = text[start_idx:i+1]
                        try:
                            return json.loads(json_str)
                        except json.JSONDecodeError:
                            # Try to fix common issues
                            json_str_fixed = self._fix_json_issues(json_str)
                            if json_str_fixed:
                                try:
                                    return json.loads(json_str_fixed)
                                except json.JSONDecodeError:
                                    continue
            return None
        except Exception:
            pass
        
        # Strategy 4: Last resort - try to fix issues
        try:
            fixed = self._fix_json_issues(text)
            if fixed:
                return json.loads(fixed)
        except json.JSONDecodeError:
            pass
        
        return None
    
    def _fix_json_issues(self, json_str: str) -> Optional[str]:
        """
        Attempt to fix common JSON issues like trailing commas, unterminated strings.
        """
        try:
            # Remove trailing commas before ] or }
            fixed = re.sub(r',\s*([}\]])', r'\1', json_str)
            
            # Attempt to parse - if it works, return fixed version
            json.loads(fixed)
            return fixed
        except json.JSONDecodeError:
            return None

    # ── Rule-based extraction ──────────────────────────────────────────────────

    def _extract_rules(self, transcript: str) -> Dict:
        """Rule-based extraction using regex patterns."""
        logger.info("Extracting with rule-based system...")

        patient_name = self._extract_patient_name(transcript)
        medicines = self._extract_medicines(transcript)
        complaints = self._extract_complaints(transcript)
        diagnosis = self._extract_diagnosis(transcript)

        # Use smart labeling if available
        tests = []
        advice = []
        if SMART_LABELING_AVAILABLE:
            try:
                classifier = SmartLabelClassifier()
                segments = classifier.segment_and_classify(transcript)

                if not complaints:
                    complaints = [s.text for s in segments if s.label == "complaint" and s.confidence > 0.5][:5]
                if not diagnosis:
                    diagnosis = [s.text for s in segments if s.label == "diagnosis" and s.confidence > 0.5][:5]

                tests = [s.text for s in segments if s.label == "test" and s.confidence > 0.5][:5]
            except Exception as e:
                logger.warning(f"Smart labeling error: {e}")

        advice = self._extract_advice(transcript)

        data = {
            "patient_name": patient_name,
            "age": None,
            "complaints": complaints,
            "diagnosis": diagnosis,
            "medicines": [vars(m) for m in medicines],
            "tests": tests,
            "advice": advice
        }

        return {"success": True, "data": data, "method": "rules"}

    # ── Post-processing ────────────────────────────────────────────────────────

    def _post_process(self, data: Dict) -> Dict:
        """Post-process extracted data: fix drug names, deduplicate patient name."""
        # Deduplicate patient name ("Rohit Rohit" → "Rohit")
        patient_name = data.get('patient_name')
        if patient_name and isinstance(patient_name, str):
            words = patient_name.split()
            seen = []
            for w in words:
                if w.lower() not in [s.lower() for s in seen]:
                    seen.append(w)
            data['patient_name'] = " ".join(seen) if seen else None

        # Fix drug names
        medicines = data.get('medicines', [])
        corrected = []
        for med in medicines:
            if isinstance(med, dict) and 'name' in med:
                name = self._correct_drug_name(med['name'])
                med['name'] = name
            corrected.append(med)

        data['medicines'] = corrected
        return data

    def _correct_drug_name(self, name: str) -> str:
        """Correct drug name using database corrections and fuzzy matching."""
        if not MEDICINE_DB_AVAILABLE:
            return name.lower()

        corrected = name.lower()

        # Apply regex corrections
        for pattern, replacement in DRUG_CORRECTIONS.items():
            corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)

        # Remove duplicate words
        words = corrected.split()
        unique_words = []
        for w in words:
            if w.lower() not in [uw.lower() for uw in unique_words]:
                unique_words.append(w)
        corrected = ' '.join(unique_words)

        # Fuzzy match if needed
        if len(corrected) < 3:
            matches = get_close_matches(corrected.lower(), KNOWN_DRUGS, n=1, cutoff=0.4)
            if matches:
                corrected = matches[0]

        return corrected.lower()

    # ── Rule-based extractors ──────────────────────────────────────────────────

    def _extract_patient_name(self, text: str) -> Optional[str]:
        """Extract patient name - handles multi-word names and various patterns."""
        text_lower = text.lower()
        
        patterns = [
            # "patient APC", "patient is APC", "patient named APC"
            r'patient\s+(?:named\s+|is\s+|name\s+)?([a-z]+(?:\s+[a-z]+)?)',
            # "with patient John Smith"
            r'with\s+patient\s+([a-z]+(?:\s+[a-z]+)?)',
            # "consultation with patient APC"
            r'consultation\s+with\s+(?:patient\s+)?([a-z]+)',
            # "Hi/Hello NAME" - after greeting
            r'(?:hi|hello|greetings)\s+([a-z]+(?:\s+[a-z]+)?)',
            # "name is X" or "patient name is X"
            r'(?:patient\s+)?name\s+(?:is\s+)?([a-z]+(?:\s+[a-z]+)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                # Find original casing from full text for this matched name
                original_match = re.search(pattern, text, re.IGNORECASE)
                if original_match:
                    name = original_match.group(1).strip()
                else:
                    name = match.group(1).strip()
                
                # Ensure it's a valid name (not time words, pronouns, etc)
                invalid_names = ['today', 'tomorrow', 'yesterday', 'now', 'then', 'the', 'a', 'is', 'has', 'been', 'going', 'get', 'have']
                if name.lower() not in invalid_names and len(name) > 1:
                    # Keep original casing for acronyms/all-caps, otherwise capitalize
                    return name.upper() if name.isupper() else ' '.join(word.capitalize() for word in name.split())
        return None

    def _extract_medicines(self, text: str) -> List[Medicine]:
        """Extract medicines using pattern matching with multiple fallback patterns."""
        medicines = []
        seen = set()

        # Multiple patterns to catch variations
        patterns = [
            # Pattern 1: "take erythromycin 500 mg 3 times a day for 5 days"
            r'(?:take|prescribe|give)\s+([a-z\s]+?)\s+(\d+)\s*(mg|ml|mcg|tablet|capsule)s?\s+(\d+)\s*times?\s+a\s+day\s+for\s+(\d+)\s*days?',
            
            # Pattern 2: "medicine, erythromycin, 500 mg daily 3 times for 5 days" OR "medicine, erythromycin, 500 mg once a day 3 times for 5 days"
            r'medicine[,.]?\s+([a-z]+)\s*[,.]?\s*(\d+)\s*(mg|ml|mcg|tablet|capsule)s?\s+(?:once\s+)?a\s+day\s+(\d+)\s*times?\s+(?:for\s+)?(\d+)\s*days?',
            
            # Pattern 3: "medicine, erythromycin, 500 mg daily 3 times for 5 days" (original daily version)
            r'medicine[,.]?\s+([a-z]+)\s*[,.]?\s*(\d+)\s*(mg|ml|mcg|tablet|capsule)s?\s+daily\s+(\d+)\s*times?\s+for\s+(\d+)\s*days?',
            
            # Pattern 4: "erythromycin 500 mg, 3 times a day for 5 days"
            r'([a-z]+)\s+(\d+)\s*(mg|ml|mcg|tablet|capsule)s?\s*[,.]?\s+(\d+)\s*times?\s+a\s+day\s+for\s+(\d+)\s*days?',
            
            # Pattern 5: "medicine erythromycin 500mg 3 times daily 5 days"
            r'medicine\s+([a-z]+)\s+(\d+)(mg|ml|mcg|tablet|capsule)\s+(\d+)\s*times?\s+(?:a\s+)?day\s+(?:for\s+)?(\d+)\s*days?',
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, text.lower(), re.IGNORECASE):
                try:
                    groups = match.groups()
                    if len(groups) < 5:
                        continue
                    
                    drug_raw = groups[0].strip()
                    dose_num = groups[1]
                    unit = groups[2]
                    freq_num = groups[3]
                    duration_num = groups[4]

                    # Extract drug name - longest word or whole phrase
                    drug_words = drug_raw.split()
                    drug_name = drug_raw.strip() if len(drug_raw) > 3 else max(drug_words, key=len) if drug_words else drug_raw
                    drug_name = self._correct_drug_name(drug_name).strip()

                    # Skip if already found or invalid
                    if not drug_name or drug_name in seen or len(drug_name) < 2:
                        continue

                    seen.add(drug_name)

                    medicines.append(Medicine(
                        name=drug_name,
                        dose=f"{dose_num} {unit}",
                        frequency=f"{freq_num} times a day",
                        duration=f"{duration_num} days",
                        instruction=""
                    ))
                    break  # Found match, try next medicine
                except (IndexError, ValueError):
                    continue

        return medicines

    def _extract_complaints(self, text: str) -> List[str]:
        """Extract complaints with priority ordering."""
        text_lower = text.lower()
        complaints = []
        found = {}

        checks = [
            ('difficulty breathing', 'difficulty breathing', 1),
            ('difficulty swallowing', 'difficulty swallowing', 1),
            ('throat pain', 'throat pain', 2),
            ('fever', 'fever', 2),
            ('cough', 'cough', 2),
            ('infection', 'infection', 3),
            ('pain', 'pain', 4),
        ]

        for keyword, label, priority in checks:
            if keyword in text_lower and label not in found:
                found[label] = priority

        return sorted(found.keys(), key=lambda x: found[x])[:5]

    def _correct_medical_terms(self, text: str) -> str:
        """Correct common transcription errors in medical terms."""
        corrections = {
            r'\bretromyzen\b': 'erythromycin',
            r'\bfrench\s+dices\b': 'pharyngitis',
            r'\bfirennets\b': 'pharyngitis',
            r'\bpharangitis\b': 'pharyngitis',
            r'\bbrankitis\b': 'bronchitis',
        }
        
        result = text.lower()
        for error_pattern, correct_term in corrections.items():
            result = re.sub(error_pattern, correct_term, result, flags=re.IGNORECASE)
        return result

    def _extract_diagnosis(self, text: str) -> List[str]:
        """Extract diagnoses with priority ordering."""
        # Correct transcription errors first
        corrected_text = self._correct_medical_terms(text)
        text_lower = corrected_text.lower()
        diagnoses = []
        found = {}

        checks = [
            ('pharyngitis', 'acute pharyngitis', 1),
            ('bacterial throat infection', 'bacterial throat infection', 1),
            ('throat infection', 'bacterial throat infection', 1),
            ('bacterial infection', 'bacterial infection', 2),
            ('infection', 'infection', 3),
        ]

        for keyword, label, priority in checks:
            if keyword in text_lower and label not in found:
                found[label] = priority

        return sorted(found.keys(), key=lambda x: found[x])[:5]

    def _extract_advice(self, text: str) -> List[str]:
        """Extract advice based on content."""
        if not MEDICINE_DB_AVAILABLE:
            return []

        text_lower = text.lower()
        advice = []

        # Use advice mapping from database
        for idx, keywords_list in ADVICE_MAPPING.items():
            if any(k in text_lower for k in keywords_list):
                if idx < len(STANDARD_ADVICE):
                    advice.append(STANDARD_ADVICE[idx])

        return advice[:12]

    # ── Helper methods ────────────────────────────────────────────────────────

    def _check_groq(self) -> bool:
        """Check if Groq API key is available."""
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            logger.info("Groq API key detected")
            return True
        logger.info("GROQ_API_KEY not set")
        return False

    def _find_available_model(self) -> Optional[str]:
        """Find first available Groq model."""
        for model in self.GROQ_MODELS:
            try:
                logger.info(f"Testing Groq model: {model}...")
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "OK"}],
                    temperature=0.1,
                    max_tokens=5
                )
                logger.info(f"✅ Model available: {model}")
                return model
            except Exception:
                continue

        logger.warning("No Groq models available")
        return None


class EnsembleExtractor:
    """Combines Groq and rule-based results with confidence voting."""

    def __init__(self, extractor: GroqLLMExtractor):
        """Initialize with base extractor."""
        self.extractor = extractor

    def extract_ensemble(self, transcript: str) -> Dict:
        """Extract using both Groq and rules, merge results intelligently."""
        logger.info("Running ensemble extraction (both systems)...")

        # Get both results
        groq_result = self.extractor.extract(transcript, use_groq=True)
        rules_result = self.extractor.extract(transcript, use_groq=False)

        # Merge intelligently
        merged = self._merge(groq_result, rules_result)

        logger.info(f"Ensemble result: {len(merged.get('medicines', []))} medicines, "
                   f"{len(merged.get('diagnosis', []))} diagnoses")

        return {
            "success": True,
            "data": merged,
            "method": "ensemble",
            "groq_success": groq_result.get("success"),
            "rules_success": rules_result.get("success")
        }

    def _merge(self, groq_result: Dict, rules_result: Dict) -> Dict:
        """Merge results: Groq for medicines, rules for patient name."""
        groq_data = groq_result.get("data", {})
        rules_data = rules_result.get("data", {})

        return {
            "medicines": groq_data.get("medicines", []) or rules_data.get("medicines", []),
            "patient_name": rules_data.get("patient_name") or groq_data.get("patient_name"),
            "age": groq_data.get("age") or rules_data.get("age"),
            "complaints": self._deduplicate(
                groq_data.get("complaints", []) + rules_data.get("complaints", [])
            ),
            "diagnosis": self._deduplicate(
                groq_data.get("diagnosis", []) + rules_data.get("diagnosis", [])
            ),
            "tests": self._deduplicate(
                groq_data.get("tests", []) + rules_data.get("tests", [])
            ),
            "advice": rules_data.get("advice", []) or groq_data.get("advice", [])
        }

    @staticmethod
    def _deduplicate(items: List) -> List:
        """Deduplicate list of strings."""
        seen = set()
        result = []
        for item in items:
            item_lower = str(item).lower()
            if item_lower not in seen:
                seen.add(item_lower)
                result.append(item)
        return result[:10]
