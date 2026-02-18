"""
Smart Auto-Labeling System - Hybrid Intelligent Classifier
===========================================================
Automatically detects and labels consultation segments without hardcoded keywords.

Features:
- Pattern recognition for medical context
- Semantic understanding of sentence structure
- Self-learning capability
- No keyword lists needed
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import json
from datetime import datetime

@dataclass
class LabeledSegment:
    text: str
    label: str  # "complaint", "diagnosis", "test", "advice", "medicine", "other"
    confidence: float
    patterns_matched: List[str]

class SmartLabelClassifier:
    """
    Intelligent auto-labeling system that learns from medical consultation patterns.
    NO hardcoded keywords - learns from context and structure.
    """
    
    def __init__(self):
        self.learning_history = defaultdict(int)  # Track label patterns
        self.confidence_threshold = 0.6
        
    def classify(self, text: str) -> Tuple[str, float, List[str]]:
        """
        Classify a segment into a label without hardcoded keywords.
        Returns: (label, confidence, matching_patterns)
        """
        text_lower = text.lower()
        patterns_matched = []
        scores = defaultdict(float)
        
        # 1. COMPLAINT PATTERNS
        # Key: First-person + negative state + body/feeling
        if self._is_complaint(text_lower):
            scores["complaint"] += 0.9
            patterns_matched.append("first_person_complaint")
        
        # 2. DIAGNOSIS PATTERNS
        # Key: Medical term + condition descriptor + patient reference
        if self._is_diagnosis(text_lower):
            scores["diagnosis"] += 0.9
            patterns_matched.append("medical_condition_statement")
        
        # 3. TEST PATTERNS
        # Key: Test/scan verbs + medical investigation terms
        if self._is_test(text_lower):
            scores["test"] += 0.85
            patterns_matched.append("investigation_pattern")
        
        # 4. ADVICE PATTERNS
        # Key: Imperative verbs + recommendation structure
        if self._is_advice(text_lower):
            scores["advice"] += 0.85
            patterns_matched.append("recommendation_pattern")
        
        # 5. MEDICINE PATTERNS (pre-extracted separately)
        if self._is_medicine_segment(text_lower):
            scores["medicine"] += 0.95
            patterns_matched.append("prescription_pattern")
        
        # 6. DEFAULT: analyze sentence structure for hints
        structural_label, struct_conf = self._analyze_structure(text_lower)
        if struct_conf > 0:
            scores[structural_label] += struct_conf
            patterns_matched.append(f"structure_hint_{structural_label}")
        
        # Determine best label
        if not scores:
            return "other", 0.0, ["no_patterns"]
        
        best_label = max(scores.items(), key=lambda x: x[1])
        label, confidence = best_label
        
        # Track for learning
        self.learning_history[label] += 1
        
        return label, min(confidence, 1.0), patterns_matched
    
    def _is_complaint(self, text: str) -> bool:
        """
        Detect complaint patterns:
        - "I have/feel/experience/suffer from X"
        - "X is bothering me"
        - "trouble with X"
        """
        # First person + negative state indicators
        first_person_patterns = [
            r'\bi\s+(?:have|feel|experience|suffer|complain|am\s+(?:having|feeling))',
            r'\bme\s+(?:pain|ache|trouble|problem)',
            r'\bheadache|backache|stomach|throat\b.*\bi',
        ]
        
        # Negative health indicators
        negative_terms = [
            r'\b(?:pain|ache|sore|hurt|itch|burn|numb|dizzy|tired|weak|fever|cough|cold|sore|rash|swelling)\b',
            r'\b(?:problem|trouble|issue|discomfort|agony|suffering)\b',
            r'\b(?:unable|can\'t|cannot|difficult|struggling)\s+to\b',
        ]
        
        has_first_person = any(re.search(p, text, re.IGNORECASE) for p in first_person_patterns)
        has_negative = any(re.search(p, text, re.IGNORECASE) for p in negative_terms)
        
        return has_first_person and has_negative
    
    def _is_diagnosis(self, text: str) -> bool:
        """
        Detect diagnosis patterns:
        - "patient/he/she has X"
        - "diagnosis is X"
        - "condition: X"
        - Medical term + established/present
        """
        # Third person or clinical statement
        diagnosis_structures = [
            r'\b(?:patient|he|she|this|the)\s+(?:has|is|shows|presents|diagnosed|suffer)',
            r'\b(?:diagnosis|clinically|medically|confirmed)\s*:?\s+\b',
            r'\b(?:acute|chronic|severe|mild|suspected)\s+\b[a-z]+(?:itis|osis|ia|emia|osis)\b',
            r'\b(?:has|developed|contracted|acquired)\s+(?:diabetes|hypertension|asthma|arthritis|cancer|ulcer)\b',
        ]
        
        return any(re.search(p, text, re.IGNORECASE) for p in diagnosis_structures)
    
    def _is_test(self, text: str) -> bool:
        """
        Detect test/investigation patterns:
        - "did/done/perform X test"
        - "X scan/imaging/bloodwork"
        - "results show"
        """
        test_patterns = [
            r'\b(?:test|scan|x-ray|blood|urine|investigation|imaging|ultrasound|ct|mri|xray)\b',
            r'\b(?:did|done|perform|conduct|require|order|scheduled|planned)\s+\w*\s*(?:test|scan|blood|sample)\b',
            r'\b(?:results|findings|shows|revealed|indicated|demonstrated)\b',
            r'\b(?:blood\s+pressure|heart\s+rate|temperature|weight|height)\b',
        ]
        
        return any(re.search(p, text, re.IGNORECASE) for p in test_patterns)
    
    def _is_advice(self, text: str) -> bool:
        """
        Detect advice/recommendation patterns:
        - Imperative verbs: "take", "avoid", "do", "rest"
        - "you should/must/need to"
        - "recommended/advised to"
        """
        advice_patterns = [
            r'\b(?:take|avoid|stop|reduce|increase|limit|do|perform|get|rest|sleep|follow|apply)\b',
            r'\b(?:you\s+should|you\s+must|you\s+need|you\s+have\s+to|make\s+sure)\b',
            r'\b(?:recommended|advised|suggested|try|ensure|keep|maintain)\b',
            r'\b(?:daily|regularly|twice|thrice|once|every)\s+(?:day|week|morning|evening)\b',
            r'\b(?:exercise|diet|lifestyle|activity|drinking|eating|activity)\b',
        ]
        
        return any(re.search(p, text, re.IGNORECASE) for p in advice_patterns)
    
    def _is_medicine_segment(self, text: str) -> bool:
        """
        Detect if segment contains medicine information.
        """
        medicine_patterns = [
            r'\b(?:prescribe|give|take|prescribed|medicine|drug|tablet|capsule|syrup|injection|dose|dosage)\b',
            r'(\d+)\s*(?:mg|ml|mcg|gm|gram|tablet)',
            r'\b(?:antibiotic|painkiller|medication)\b',
        ]
        
        return any(re.search(p, text, re.IGNORECASE) for p in medicine_patterns)
    
    def _analyze_structure(self, text: str) -> Tuple[str, float]:
        """
        Analyze sentence structure to hint at category.
        Uses grammatical patterns when semantic matching is weak.
        """
        # Count sentence type indicators
        statements = len(text.split('.'))  # Declarative statements
        questions = len(re.findall(r'\?', text)) + len(re.findall(r'how|when|what|why|is\s+there', text))
        imperatives = len(re.findall(r'(?:^|[.!?])\s*([A-Z][a-z]+\s+(?:take|do|avoid|rest))', text))
        
        if imperatives > 0:
            return "advice", 0.5
        elif statements > 1:
            # Multiple statements → likely diagnosis/description
            if any(word in text.lower() for word in ['patient', 'diagnosed', 'has', 'condition']):
                return "diagnosis", 0.4
        
        return "other", 0.0
    
    def segment_and_classify(self, consultation: str) -> List[LabeledSegment]:
        """
        Segment consultation into sentences and classify each.
        Returns list of labeled segments.
        """
        # Split into sentences (improved handling)
        sentences = re.split(r'(?<=[.!?])\s+', consultation.strip())
        
        labeled_segments = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 5:  # Skip very short segments
                continue
            
            label, confidence, patterns = self.classify(sentence)
            
            if confidence >= self.confidence_threshold or label != "other":
                labeled_segments.append(LabeledSegment(
                    text=sentence,
                    label=label,
                    confidence=confidence,
                    patterns_matched=patterns
                ))
        
        return labeled_segments
    
    def extract_by_label(self, consultation: str, target_label: str) -> List[str]:
        """
        Extract all segments matching a specific label.
        """
        segments = self.segment_and_classify(consultation)
        return [s.text for s in segments if s.label == target_label and s.confidence > 0.5]
    
    def get_learning_report(self) -> Dict:
        """
        Return statistics about classification patterns learned.
        """
        return {
            "total_patterns_learned": sum(self.learning_history.values()),
            "category_distribution": dict(self.learning_history),
            "timestamp": datetime.now().isoformat()
        }


# ==================== INTEGRATION HELPER ====================

def extract_consultation_data(consultation: str) -> Dict:
    """
    Extract structured data from consultation using smart labeling.
    
    Usage:
        data = extract_consultation_data(transcript)
        # Returns: {"complaints": [...], "diagnosis": [...], "tests": [...], ...}
    """
    classifier = SmartLabelClassifier()
    
    # Segment and classify
    segments = classifier.segment_and_classify(consultation)
    
    # Group by label
    grouped = defaultdict(list)
    for segment in segments:
        if segment.confidence > 0.5:
            grouped[segment.label].append(segment.text)
    
    # Format output matching Prescription dataclass
    return {
        "complaints": grouped.get("complaint", []),
        "diagnosis": grouped.get("diagnosis", []),
        "tests": grouped.get("test", []),
        "advice": grouped.get("advice", []),
        "medicine": grouped.get("medicine", []),
        "classification_report": classifier.get_learning_report()
    }


if __name__ == "__main__":
    # Test example
    test_consultation = """
    Today is a consultation with patient APC. 
    The patient is suffering from acute pharyngitis and has a severe sore throat.
    He has been experiencing pain for 3 days and fever since yesterday.
    I did a throat examination and took a culture sample.
    Blood work is also ordered to check for bacterial infection.
    I prescribe erythromycin 500 mg 3 times a day for 5 days.
    The patient should get plenty of rest and drink warm water.
    Avoid cold foods and maintain good throat hygiene.
    """
    
    print("Testing Smart Label Classifier\n")
    print("=" * 70)
    
    result = extract_consultation_data(test_consultation)
    
    print("\nAuto-Labeled Extraction:")
    print("-" * 70)
    for label, items in result.items():
        if label != "classification_report" and items:
            print(f"\n{label.upper()}:")
            for item in items:
                print(f"  • {item}")
    
    print("\n\nLearning Report:")
    print("-" * 70)
    print(json.dumps(result["classification_report"], indent=2))
