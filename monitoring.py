"""
MONITORING & AUDIT LOGGING LAYER
Tracks system performance, errors, and compliance
"""

import json
import logging
import sqlite3
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """Track system-level metrics"""
    timestamp: str
    whisper_confidence: float
    language_detection_confidence: float
    extraction_success: bool
    extraction_method: str
    validation_passed: bool
    doctor_approved: bool
    processing_time_ms: float
    model_version: str = "v2.1"

class MonitoringEngine:
    """Production monitoring for hospitals"""
    
    def __init__(self, db_file: str = "audit_logs.db"):
        self.db_file = db_file
        self._init_audit_db()
        self.metrics_buffer = []
        
    def _init_audit_db(self):
        """Create audit logging tables"""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT,
                    user_id TEXT,
                    action TEXT,
                    resource TEXT,
                    details TEXT,
                    ip_address TEXT,
                    status TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT,
                    whisper_confidence REAL,
                    language_confidence REAL,
                    extraction_method TEXT,
                    validation_passed BOOLEAN,
                    doctor_approved BOOLEAN,
                    processing_time_ms REAL
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS error_logs (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT,
                    component TEXT,
                    error_type TEXT,
                    error_message TEXT,
                    stack_trace TEXT,
                    severity TEXT
                )
            ''')
            conn.commit()
    
    def log_audit_event(self, user_id: str, action: str, resource: str, details: Dict, 
                       status: str = "success") -> int:
        """Log audit event for compliance"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.execute('''
                INSERT INTO audit_logs 
                (timestamp, user_id, action, resource, details, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                user_id,
                action,
                resource,
                json.dumps(details),
                status
            ))
            conn.commit()
            return cursor.lastrowid
    
    def log_error(self, component: str, error_type: str, error_msg: str, 
                 stack_trace: str = "", severity: str = "ERROR"):
        """Log system errors for debugging"""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute('''
                INSERT INTO error_logs 
                (timestamp, component, error_type, error_message, stack_trace, severity)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                component,
                error_type,
                error_msg,
                stack_trace,
                severity
            ))
            conn.commit()
        
        logger.error(f"[{component}] {error_type}: {error_msg}")
    
    def record_metrics(self, metrics: SystemMetrics):
        """Record performance metrics"""
        self.metrics_buffer.append(metrics)
        
        if len(self.metrics_buffer) >= 10:  # Batch insert
            self._flush_metrics()
    
    def _flush_metrics(self):
        """Batch insert metrics"""
        if not self.metrics_buffer:
            return
            
        with sqlite3.connect(self.db_file) as conn:
            for m in self.metrics_buffer:
                conn.execute('''
                    INSERT INTO system_metrics
                    (timestamp, whisper_confidence, language_confidence, 
                     extraction_method, validation_passed, doctor_approved, processing_time_ms)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    m.timestamp,
                    m.whisper_confidence,
                    m.language_detection_confidence,
                    m.extraction_method,
                    m.validation_passed,
                    m.doctor_approved,
                    m.processing_time_ms
                ))
            conn.commit()
        
        self.metrics_buffer = []
        logger.info(f"📊 Flushed metrics batch")
    
    def get_health_report(self) -> Dict[str, Any]:
        """Generate system health report"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            # Last 24 hours stats
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    AVG(whisper_confidence) as avg_whisper,
                    AVG(language_confidence) as avg_lang_detect,
                    SUM(CASE WHEN validation_passed=1 THEN 1 ELSE 0 END) as validation_ok,
                    SUM(CASE WHEN doctor_approved=1 THEN 1 ELSE 0 END) as approved,
                    AVG(processing_time_ms) as avg_time_ms
                FROM system_metrics
                WHERE datetime(timestamp) >= datetime('now', '-1 day')
            ''')
            
            stats = cursor.fetchone()
            
            return {
                'period': 'Last 24 hours',
                'total_prescriptions': stats[0] or 0,
                'avg_whisper_confidence': round(stats[1] or 0, 3),
                'avg_language_confidence': round(stats[2] or 0, 3),
                'validation_success_rate': f"{(stats[3] or 0) / max((stats[0] or 1), 1) * 100:.1f}%",
                'doctor_approval_rate': f"{(stats[4] or 0) / max((stats[0] or 1), 1) * 100:.1f}%",
                'avg_processing_time_ms': round(stats[5] or 0, 1)
            }

# Structured logging formatter
class StructuredFormatter(logging.Formatter):
    """Format logs as JSON for aggregation"""
    
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'module': record.module,
            'message': record.getMessage(),
        }
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)
