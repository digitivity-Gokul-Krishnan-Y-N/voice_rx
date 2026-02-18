"""
DOCTOR REVIEW & APPROVAL SYSTEM
Critical bridge between AI extraction and medical records
"""

import json
from datetime import datetime
from typing import Dict, Optional
import sqlite3
import uuid

class DoctorReviewUI:
    """
    Provides doctor review interface for prescriptions
    Before saving to DB, doctor must approve
    """
    
    def __init__(self, db_file: str = "prescriptions.db"):
        self.db_file = db_file
        self._init_review_table()
    
    def _init_review_table(self):
        """Create review tracking table"""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS prescription_reviews (
                    review_id TEXT PRIMARY KEY,
                    prescription_data TEXT,
                    doctor_id TEXT,
                    doctor_name TEXT,
                    review_timestamp TEXT,
                    status TEXT,
                    approved BOOLEAN,
                    modifications TEXT,
                    signature TEXT
                )
            ''')
            conn.commit()
    
    def create_review_request(self, prescription_dict: Dict) -> str:
        """
        Create a review session for doctor
        Returns review_id
        """
        review_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_file) as conn:
            conn.execute('''
                INSERT INTO prescription_reviews
                (review_id, prescription_data, status)
                VALUES (?, ?, ?)
            ''', (
                review_id,
                json.dumps(prescription_dict, indent=2),
                'pending_review'
            ))
            conn.commit()
        
        return review_id
    
    def display_review_screen(self, prescription_dict: Dict) -> str:
        """
        Display prescription for doctor review
        HTML formatted for web interface
        """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Prescription Review - {prescription_dict.get('patient_name', 'Unknown')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .prescription {{ border: 2px solid #4CAF50; padding: 20px; border-radius: 5px; }}
                .editable {{ background-color: #fffacd; padding: 10px; margin: 5px 0; }}
                button {{ padding: 10px 20px; margin: 5px; cursor: pointer; }}
                .approve {{ background-color: #4CAF50; color: white; }}
                .reject {{ background-color: #f44336; color: white; }}
                .warning {{ background-color: #ff9800; padding: 10px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <h1>PRESCRIPTION REVIEW & APPROVAL</h1>
            <h2>{prescription_dict.get('patient_name', 'Unknown')} (Age: {prescription_dict.get('age', 'N/A')})</h2>
            
            <div class="prescription">
                <h3>📋 Extracted Prescription</h3>
                
                <h4>Diagnosis:</h4>
                <ul>
        """
        
        for diag in prescription_dict.get('diagnosis', []):
            html += f"<li>{diag}</li>"
        
        html += """</ul>
                <h4>Medicines:</h4>
                <div class="editable">
        """
        
        for i, med in enumerate(prescription_dict.get('medicines', [])):
            html += f"""
                    <div style="border: 1px solid #ddd; padding: 10px; margin: 5px 0;">
                        <input type="text" value="{med['name']}" id="med_{i}_name" placeholder="Medicine name"> 
                        <input type="text" value="{med['dose']}" id="med_{i}_dose" placeholder="Dose">
                        <input type="text" value="{med['frequency']}" id="med_{i}_freq" placeholder="Frequency">
                        <input type="text" value="{med['duration']}" id="med_{i}_dur" placeholder="Duration">
                        <input type="text" value="{med.get('instruction', '')}" id="med_{i}_instr" placeholder="Instructions">
                    </div>
            """
        
        html += """
                </div>
                
                <h4>Tests:</h4>
                <ul>
        """
        
        for test in prescription_dict.get('tests', []):
            html += f"<li>{test}</li>"
        
        html += """</ul>
                
                <h4>Advice:</h4>
                <ul>
        """
        
        for advice in prescription_dict.get('advice', []):
            html += f"<li>{advice}</li>"
        
        warnings = prescription_dict.get('warnings', [])
        if warnings:
            html += '<div class="warning"><strong>⚠️ System Warnings:</strong><ul>'
            for w in warnings:
                html += f"<li>{w}</li>"
            html += '</ul></div>'
        
        html += """
                </ul>
            </div>
            
            <h3>Doctor Signature & Approval</h3>
            <label>Doctor Name: <input type="text" id="doctor_name" placeholder="Full Name"></label>
            <label>Doctor ID: <input type="text" id="doctor_id" placeholder="License #"></label>
            <label>Signature: <input type="text" id="signature" placeholder="Electronic signature"></label>
            
            <div>
                <button class="approve" onclick="approveRx()">✅ APPROVE PRESCRIPTION</button>
                <button class="reject" onclick="rejectRx()">❌ REJECT & EDIT</button>
                <button onclick="history.back()">↩️ CANCEL</button>
            </div>
            
            <script>
                function approveRx() {{
                    alert('Prescription approved and saved to medical records');
                    // Send approval to backend
                }}
                
                function rejectRx() {{
                    alert('Please make corrections above and resubmit');
                }}
            </script>
        </body>
        </html>
        """
        
        return html
    
    def approve_prescription(self, review_id: str, doctor_name: str, doctor_id: str, 
                           modifications: Dict = None) -> bool:
        """Doctor approves prescription"""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute('''
                UPDATE prescription_reviews
                SET status = ?, approved = ?, doctor_name = ?, doctor_id = ?, 
                    review_timestamp = ?, modifications = ?
                WHERE review_id = ?
            ''', (
                'approved',
                True,
                doctor_name,
                doctor_id,
                datetime.now().isoformat(),
                json.dumps(modifications or {}),
                review_id
            ))
            conn.commit()
        
        return True
    
    def reject_prescription(self, review_id: str, reason: str) -> bool:
        """Doctor rejects prescription for corrections"""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute('''
                UPDATE prescription_reviews
                SET status = ?, approved = ?, review_timestamp = ?
                WHERE review_id = ?
            ''', (
                f'rejected: {reason}',
                False,
                datetime.now().isoformat(),
                review_id
            ))
            conn.commit()
        
        return False
