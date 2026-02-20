"""
Metrics Module: Logging dashboard and system metrics for production monitoring.

MetricsCollector: Tracks extraction quality, performance, and routing decisions
MetricsDashboard: Displays real-time metrics summary
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict, field
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class ExtractionMetrics:
    """Metrics for a single extraction."""
    audio_file: str
    timestamp: str
    transcription_tier: int
    transcript_length: int
    cleaned_length: int = 0  # Length after cleaning
    transcript_was_modified: bool = False  # Whether cleaning made changes
    detected_language: str = "en"
    routing_quality_score: float = 0.0
    routing_decision: str = "unknown"
    extraction_method: str = "rules"
    medicines_extracted: int = 0
    diagnosis_extracted: int = 0
    validation_passed: bool = False
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)
    confidence: float = 0.0
    processing_time_sec: float = 0.0


class MetricsCollector:
    """Collects and aggregates extraction metrics for monitoring."""

    def __init__(self):
        """Initialize metrics storage."""
        self.metrics: List[ExtractionMetrics] = []
        self.start_time = datetime.now()

    def record(self, metrics: ExtractionMetrics) -> None:
        """Record extraction metrics."""
        self.metrics.append(metrics)
        logger.debug(f"Recorded metrics for {metrics.audio_file}")

    def get_summary(self) -> Dict[str, Any]:
        """Get aggregated metrics summary."""
        if not self.metrics:
            return {
                "total_processed": 0,
                "success_count": 0,
                "processing_time_sec": 0.0,
                "success_rate": "0%",
                "total_processing_time_sec": "0.0",
                "system_uptime_sec": "0.0",
                "avg_extraction_time_sec": "0",
                "routing_distribution": {},
                "extraction_methods": {},
                "language_distribution": {},
                "transcription_tiers": {},
                "avg_medicines_per_prescription": "0",
                "avg_diagnosis_per_prescription": "0",
                "avg_confidence": "0%",
            }

        total = len(self.metrics)
        passed = sum(1 for m in self.metrics if m.validation_passed)
        total_time = sum(m.processing_time_sec for m in self.metrics)
        uptime = (datetime.now() - self.start_time).total_seconds()

        routing_dist = defaultdict(int)
        extraction_dist = defaultdict(int)
        lang_dist = defaultdict(int)
        tier_dist = defaultdict(int)

        for m in self.metrics:
            routing_dist[m.routing_decision] += 1
            extraction_dist[m.extraction_method] += 1
            lang_dist[m.detected_language] += 1
            tier_dist[f"tier_{m.transcription_tier}"] += 1

        return {
            "total_processed": total,
            "success_count": passed,
            "success_rate": f"{(passed / total * 100):.1f}%" if total > 0 else "0%",
            "total_processing_time_sec": f"{total_time:.1f}",
            "system_uptime_sec": f"{uptime:.1f}",
            "avg_extraction_time_sec": f"{(total_time / total):.1f}" if total > 0 else "0",
            "routing_distribution": dict(routing_dist),
            "extraction_methods": dict(extraction_dist),
            "language_distribution": dict(lang_dist),
            "transcription_tiers": dict(tier_dist),
            "avg_medicines_per_prescription": f"{(sum(m.medicines_extracted for m in self.metrics) / total):.1f}" if total > 0 else "0",
            "avg_diagnosis_per_prescription": f"{(sum(m.diagnosis_extracted for m in self.metrics) / total):.1f}" if total > 0 else "0",
            "avg_confidence": f"{(sum(m.confidence for m in self.metrics) / total):.0%}" if total > 0 else "0%",
        }

    def export_json(self, filename: str) -> None:
        """Export metrics to JSON file."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "summary": self.get_summary(),
            "records": [asdict(m) for m in self.metrics]
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Exported metrics to {filename}")


class MetricsDashboard:
    """Display real-time metrics dashboard."""

    @staticmethod
    def display(collector: MetricsCollector) -> None:
        """Display formatted metrics dashboard."""
        summary = collector.get_summary()

        output = [
            "\n" + "=" * 80,
            "MEDICAL SYSTEM METRICS DASHBOARD",
            "=" * 80,
            f"Timestamp: {datetime.now().isoformat()}",
            "",
            "PROCESSING STATISTICS",
            "-" * 80,
            f"  Total Processed: {summary['total_processed']}",
            f"  Success Rate: {summary['success_rate']}",
            f"  Avg Processing Time: {summary['avg_extraction_time_sec']} sec",
            f"  System Uptime: {summary['system_uptime_sec']} sec",
            "",
            "EXTRACTION QUALITY",
            "-" * 80,
            f"  Avg Medicines/Prescription: {summary['avg_medicines_per_prescription']}",
            f"  Avg Diagnoses/Prescription: {summary['avg_diagnosis_per_prescription']}",
            f"  Avg Confidence Score: {summary['avg_confidence']}",
            "",
            "ROUTING DISTRIBUTION",
            "-" * 80,
        ]

        for route, count in summary['routing_distribution'].items():
            percentage = (count / summary['total_processed'] * 100) if summary['total_processed'] > 0 else 0
            output.append(f"  {route}: {count} ({percentage:.1f}%)")

        output.extend([
            "",
            "EXTRACTION METHODS",
            "-" * 80,
        ])

        for method, count in summary['extraction_methods'].items():
            percentage = (count / summary['total_processed'] * 100) if summary['total_processed'] > 0 else 0
            output.append(f"  {method}: {count} ({percentage:.1f}%)")

        output.extend([
            "",
            "LANGUAGE DISTRIBUTION",
            "-" * 80,
        ])

        for lang, count in summary['language_distribution'].items():
            percentage = (count / summary['total_processed'] * 100) if summary['total_processed'] > 0 else 0
            output.append(f"  {lang.upper()}: {count} ({percentage:.1f}%)")

        output.extend([
            "",
            "TRANSCRIPTION TIERS",
            "-" * 80,
        ])

        for tier, count in summary['transcription_tiers'].items():
            percentage = (count / summary['total_processed'] * 100) if summary['total_processed'] > 0 else 0
            output.append(f"  {tier}: {count} ({percentage:.1f}%)")

        output.append("=" * 80 + "\n")

        # Print and log
        dashboard_text = "\n".join(output)
        print(dashboard_text)
        logger.info(dashboard_text)
