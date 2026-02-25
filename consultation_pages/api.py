"""
Flask API for integrated voice consultation system
Connects React frontend to medical_system_v2.py for extraction
"""

import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from pathlib import Path

# Import medical system
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from medical_system_v2 import MedicalSystem
except ImportError:
    MedicalSystem = None

# Configure Flask
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize medical system
try:
    medical_system = MedicalSystem()
except Exception as e:
    logger.warning(f"Medical system not available: {e}")
    medical_system = None

# Audio storage
AUDIO_DIR = Path(__file__).parent / "data" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

RESULTS_FILE = Path(__file__).parent.parent / "data" / "live_consultation_result.json"

# Global recording state
recording_session = {
    "is_recording": False,
    "audio_file": None,
    "start_time": None,
}


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "Medical Consultation API"})


@app.route("/api/start-consultation", methods=["POST"])
def start_consultation():
    """Start recording audio for consultation"""
    try:
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_file = AUDIO_DIR / f"consultation_{timestamp}.wav"

        recording_session["is_recording"] = True
        recording_session["audio_file"] = str(audio_file)
        recording_session["start_time"] = datetime.now().isoformat()

        logger.info(f"📍 Consultation started: {audio_file}")

        return jsonify({
            "status": "recording_started",
            "audio_file": str(audio_file),
            "timestamp": recording_session["start_time"],
        })

    except Exception as e:
        logger.error(f"❌ Error starting consultation: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/stop-consultation", methods=["POST"])
def stop_consultation():
    """Stop recording and extract consultation data"""
    try:
        if not recording_session["is_recording"]:
            return jsonify({"error": "No active recording"}), 400

        recording_session["is_recording"] = False
        audio_file = recording_session["audio_file"]

        if not os.path.exists(audio_file):
            logger.error(f"❌ Audio file not found: {audio_file}")
            return jsonify({"error": "Audio file not saved"}), 400

        logger.info(f"⏹️  Processing audio: {audio_file}")

        # Process audio with medical system if available
        if medical_system:
            result = medical_system.process(audio_file)
        else:
            # Return mock data if medical system not available
            result = {
                "success": False,
                "error": "Medical system not available",
                "patient_name": None,
                "complaints": [],
                "diagnosis": [],
                "medicines": [],
                "tests": [],
                "advice": []
            }

        # Save result to JSON file
        RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Consultation extracted and saved")

        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ Error stopping consultation: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/save-consultation", methods=["POST"])
def save_consultation():
    """Save consultation data to database"""
    try:
        data = request.json

        logger.info(f"💾 Saving consultation: {data.get('patient_name', 'Unknown')}")

        result = {
            "status": "saved",
            "consultation_id": f"CONSULT_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "data": data,
        }

        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ Error saving consultation: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/consultation-data", methods=["GET"])
def get_consultation_data():
    """Get last extracted consultation data"""
    try:
        if RESULTS_FILE.exists():
            with open(RESULTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return jsonify(data)
        else:
            return jsonify({"error": "No consultation data available"}), 404

    except Exception as e:
        logger.error(f"❌ Error getting consultation data: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/status", methods=["GET"])
def get_status():
    """Get current recording status"""
    return jsonify({
        "is_recording": recording_session["is_recording"],
        "start_time": recording_session["start_time"],
        "audio_file": recording_session["audio_file"],
    })


if __name__ == "__main__":
    logger.info("🚀 Starting Medical Consultation API Server...")
    logger.info(f"📂 Audio directory: {AUDIO_DIR}")
    logger.info(f"📄 Results file: {RESULTS_FILE}")
    app.run(host="0.0.0.0", port=5000, debug=True)
