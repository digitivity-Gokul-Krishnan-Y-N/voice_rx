"""
Unit Tests for Medical System Modules

Tests for transcription, routing, extraction, and validation components
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

# Import modules to test
from transcription import WhisperTranscriber, TranscriptionResult
from routing import AudioAnalyzer, RouteSelector
from extraction import GroqLLMExtractor, Medicine, EnsembleExtractor
from validation import ValidationLayer, Prescription


class TestAudioAnalyzer(unittest.TestCase):
    """Tests for AudioAnalyzer."""

    def setUp(self):
        self.analyzer = AudioAnalyzer()

    def test_analyze_high_quality_input(self):
        """Test analysis of high-quality medical transcript."""
        transcript = "Hi Rohit, you have a throat infection. Take Erythromycin 500 mg, 3 times a day for 5 days."
        metrics = self.analyzer.analyze(
            transcript=transcript,
            whisper_confidence=0.9,
            language="en",
            language_confidence=0.85
        )

        self.assertGreater(metrics['overall_quality'], 0.5)
        self.assertGreater(metrics['has_medical_keywords'], 0.1)
        self.assertEqual(metrics['detected_language'], 'en')

    def test_analyze_truncated_input(self):
        """Test analysis of truncated/empty transcript."""
        transcript = "..."
        metrics = self.analyzer.analyze(
            transcript=transcript,
            whisper_confidence=0.3,
            language="ta",
            language_confidence=0.1
        )

        self.assertLess(metrics['overall_quality'], 0.5)
        self.assertEqual(metrics['transcript_length'], 3)

    def test_completeness_assessment(self):
        """Test transcript completeness scoring."""
        short = "Take medicine"
        self.assertLess(self.analyzer._assess_completeness(short), 0.5)

        long = "This is a very long transcript with many sentences. " * 5
        self.assertGreaterEqual(self.analyzer._assess_completeness(long), 0.7)

    def test_medical_keyword_detection(self):
        """Test medical keyword presence detection."""
        with_keywords = "Patient has fever and infection. Prescribed Erythromycin 500 mg"
        self.assertGreater(self.analyzer._has_medical_keywords(with_keywords), 0.1)

        without_keywords = "The weather is nice today"
        self.assertEqual(self.analyzer._has_medical_keywords(without_keywords), 0.0)


class TestRouteSelector(unittest.TestCase):
    """Tests for RouteSelector."""

    def setUp(self):
        self.selector = RouteSelector()

    def test_route_high_quality_input(self):
        """Test routing for high-quality input."""
        metrics = {
            'overall_quality': 0.84,
            'detected_language': 'en',
            'has_medical_keywords': 0.4,
            'transcript_length': 1137,
        }

        route, config = self.selector.select_route(metrics)
        self.assertEqual(route, 'groq_only')

    def test_route_uncertain_input(self):
        """Test routing for uncertain quality input."""
        metrics = {
            'overall_quality': 0.60,
            'detected_language': 'en',
            'has_medical_keywords': 0.5,
            'transcript_length': 300,
        }

        route, config = self.selector.select_route(metrics)
        self.assertEqual(route, 'ensemble')

    def test_route_truncated_input(self):
        """Test routing for truncated input."""
        metrics = {
            'overall_quality': 0.2,
            'detected_language': 'ta',
            'has_medical_keywords': 0.0,
            'transcript_length': 3,
        }

        route, config = self.selector.select_route(metrics)
        self.assertEqual(route, 'rules_only')

    def test_route_poor_quality_input(self):
        """Test routing for poor quality input."""
        metrics = {
            'overall_quality': 0.3,
            'detected_language': 'en',
            'has_medical_keywords': 0.1,
            'transcript_length': 200,
        }

        route, config = self.selector.select_route(metrics)
        self.assertEqual(route, 'rules_only')


class TestGroqLLMExtractor(unittest.TestCase):
    """Tests for GroqLLMExtractor."""

    def setUp(self):
        self.extractor = GroqLLMExtractor()

    def test_extract_rules_basic(self):
        """Test rule-based extraction on simple transcript."""
        transcript = "Hi Rohit, you have a throat infection. Take Erythromycin 500 mg, 3 times a day for 5 days."
        result = self.extractor.extract(transcript, use_groq=False)

        self.assertTrue(result['success'])
        self.assertEqual(result['method'], 'rules')
        self.assertGreaterEqual(len(result['data']['medicines']), 1)

    def test_patient_name_extraction(self):
        """Test patient name extraction from greeting."""
        transcript = "Hi Rohit, you have a throat infection."
        name = self.extractor._extract_patient_name(transcript)
        self.assertIsNotNone(name)

    def test_medicine_extraction(self):
        """Test medicine extraction from transcript."""
        transcript = "Take Erythromycin 500 mg, 3 times a day for 5 days."
        medicines = self.extractor._extract_medicines(transcript)

        self.assertEqual(len(medicines), 1)
        self.assertEqual(medicines[0].name, "Erythromycin")
        self.assertEqual(medicines[0].dose, "500 mg")
        self.assertEqual(medicines[0].frequency, "3 times a day")

    def test_deduplication_in_post_process(self):
        """Test deduplication of patient name."""
        data = {
            'patient_name': 'Rohit Rohit',
            'medicines': [],
            'diagnosis': [],
            'complaints': [],
            'tests': [],
            'advice': []
        }
        result = self.extractor._post_process(data)
        self.assertEqual(result['patient_name'], 'Rohit')

    def test_drug_name_correction(self):
        """Test drug name correction."""
        incorrect = "erthromyc"
        corrected = self.extractor._correct_drug_name(incorrect)
        # Should attempt fuzzy matching or fallback to original
        self.assertIsNotNone(corrected)


class TestValidationLayer(unittest.TestCase):
    """Tests for ValidationLayer."""

    def setUp(self):
        self.validator = ValidationLayer()

    def test_validate_complete_prescription(self):
        """Test validation of complete, valid prescription."""
        prescription = Prescription(
            patient_name="Rohit",
            diagnosis=["acute pharyngitis"],
            medicines=[
                {'name': 'Erythromycin', 'dose': '500 mg', 'frequency': '3 times a day', 'duration': '5 days'}
            ]
        )

        is_valid, errors, warnings = self.validator.validate(prescription)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_missing_patient_name(self):
        """Test validation fails without patient name."""
        prescription = Prescription(
            patient_name="",
            diagnosis=["infection"],
            medicines=[{'name': 'Drug', 'dose': '100 mg', 'frequency': '1/day', 'duration': '5 days'}]
        )

        is_valid, errors, warnings = self.validator.validate(prescription)
        self.assertFalse(is_valid)
        self.assertIn("Patient name required", errors[0])

    def test_validate_invalid_dose_format(self):
        """Test validation fails with invalid dose format."""
        prescription = Prescription(
            patient_name="Rohit",
            diagnosis=["infection"],
            medicines=[
                {'name': 'Drug', 'dose': 'some amount', 'frequency': '1/day', 'duration': '5 days'}
            ]
        )

        is_valid, errors, warnings = self.validator.validate(prescription)
        self.assertFalse(is_valid)

    def test_validate_duplicate_drug_warning(self):
        """Test warning for duplicate drug."""
        prescription = Prescription(
            patient_name="Rohit",
            diagnosis=["infection"],
            medicines=[
                {'name': 'Aspirin', 'dose': '500 mg', 'frequency': '1/day', 'duration': '5 days'},
                {'name': 'Aspirin', 'dose': '500 mg', 'frequency': '2/day', 'duration': '5 days'}
            ]
        )

        is_valid, errors, warnings = self.validator.validate(prescription)
        self.assertTrue(is_valid)  # Should still be valid, just with warning
        self.assertGreater(len(warnings), 0)


class TestEnsembleExtractor(unittest.TestCase):
    """Tests for EnsembleExtractor."""

    def setUp(self):
        self.extractor = GroqLLMExtractor()
        self.ensemble = EnsembleExtractor(self.extractor)

    def test_deduplicate_lists(self):
        """Test list deduplication."""
        items = ["fever", "fever", "pain", "infection", "pain"]
        deduplicated = self.ensemble._deduplicate(items)

        self.assertEqual(len(deduplicated), 3)
        self.assertIn("fever", deduplicated)
        self.assertIn("pain", deduplicated)
        self.assertIn("infection", deduplicated)

    def test_merge_results(self):
        """Test merging of extraction results."""
        groq_result = {
            "success": True,
            "data": {
                "medicines": [{'name': 'Drug1', 'dose': '500 mg', 'frequency': '1/day', 'duration': '5 days'}],
                "diagnoses": ["infection"],
                "patient_name": None
            }
        }

        rules_result = {
            "success": True,
            "data": {
                "medicines": [],
                "diagnoses": [],
                "patient_name": "Rohit",
                "complaints": ["fever"]
            }
        }

        merged = self.ensemble._merge(groq_result, rules_result)
        self.assertEqual(len(merged['medicines']), 1)
        self.assertEqual(merged['patient_name'], 'Rohit')


# Test runner
if __name__ == '__main__':
    unittest.main(verbosity=2)
