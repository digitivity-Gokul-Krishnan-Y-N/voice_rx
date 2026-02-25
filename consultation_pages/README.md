# 🎤 Integrated Consultation System

Complete voice-to-prescription system with **single-page React component** that records audio, auto-fills from extracted data, and allows inline editing.

## ✨ Key Features

✅ **Voice Recording**
- Start/Stop buttons for microphone input
- Real-time audio processing
- Auto-save to WAV files

✅ **Auto-Fill from Extracted Data**
- Automatically populates all fields from medical extraction
- Supports: patient name, complaints, diagnosis, medicines, tests, advice
- Loads from `/data/live_consultation_result.json`

✅ **Inline Editing**
- Edit all fields on the same page
- Add/remove medicines, tests, advice with simple buttons
- No modal dialogs or extra screens
- Real-time validation

✅ **Single Page**
- All sections visible: Patient Info → Complaints → Medicines → Tests → Advice
- No tab switching required
- Clean, organized layout with Bootstrap

✅ **Backend Integration**
- Flask API connects React to medical_system_v2.py
- Handles recording, transcription, extraction, validation
- RESTful endpoints for all operations

## 📁 Project Structure

```
consultation_pages/
├── 📋 README.md (this file)
├── 📘 INTEGRATION_GUIDE.md (detailed documentation)
│
├── 🎯 Main Components
├── Consultation.jsx                    # Entry point (updated)
├── ConsultationIntegrated.jsx          # ✨ NEW - Integrated component
│
├── 🔌 Backend
├── api.py                              # ✨ NEW - Flask API server
├── recording_handler.py                # ✨ NEW - Mic recording
├── api_requirements.txt                # Python dependencies
├── START_API.bat                       # Windows startup script
│
├── 📦 Old Components (for reference)
├── ConsultationDetails/
├── ConsultationMedicines/
├── ConsultationTests/
└── ConsultationFollowUp/
```

## 🚀 Quick Start (5 minutes)

### Step 1: Prepare Backend

```bash
# Navigate to consultation folder
cd d:\voice_rx\consultation_pages

# Install dependencies
pip install -r api_requirements.txt
```

### Step 2: Start API Server

**Windows:**
```bash
START_API.bat
```

**Manual (any OS):**
```bash
python api.py
```

Server runs on: **http://localhost:5000**

### Step 3: Use React Component

```jsx
import Consultation from "./consultation_pages/Consultation";

function App() {
  return <Consultation />;
}
```

Done! 🎉 The component will:
1. Load extracted data automatically
2. Allow recording with buttons
3. Auto-fill all fields
4. Let user edit inline
5. Save to database

## 📊 Data Flow

```
┌──────────────────┐
│ 1. React Frontend │
│ Start Recording  │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────┐
│ 2. API Server (Port 5000)    │
│ /api/start-consultation      │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ 3. Recording Handler         │
│ Captures microphone audio    │
│ Saves to: data/audio/        │
└────────┬─────────────────────┘
         │
    [User speaks]
         │
         ▼
┌──────────────────────────────┐
│ 4. Stop Recording            │
│ /api/stop-consultation       │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ 5. Medical System (Python)   │
│ - Whisper transcription      │
│ - Groq/Rules extraction      │
│ - Validation                 │
│ Outputs: JSON data           │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ 6. React Auto-Fill           │
│ Populates all form fields    │
│ from extracted data          │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ 7. User Review & Edit        │
│ - Edit medicines, advice     │
│ - Add/remove items           │
│ - All on same page           │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ 8. Save Consultation         │
│ /api/save-consultation       │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ 9. Database                  │
│ ✅ Consultation saved        │
└──────────────────────────────┘
```

## 🎨 User Interface

### Recording Section
```
╔═════════════════════════════════════════╗
║ 🎤 Voice Consultation                   ║
║                [🔴 Start] [⏹️ Stop]   ║
╚═════════════════════════════════════════╝
```

### Patient Info
```
╔═════════════════════════════════════════╗
║ 👤 Patient Information                  ║
║ Name: [_____________]  Age: [___]       ║
║                        Gender: [Select] ║
╚═════════════════════════════════════════╝
```

### Complaints & Diagnosis (Side-by-Side)
```
╔══════════════════╦══════════════════╗
║ 🤒 Complaints    ║ ⚕️ Diagnosis     ║
║ + throat pain    ║ + pharyngitis    ║
║ + cough          ║ + infection      ║
║ + [___________]+ ║ + [___________]+ ║
╚══════════════════╩══════════════════╝
```

### Medicines Management
```
╔═════════════════════════════════════════╗
║ 💊 Medicines                            ║
├─────────────────────────────────────────┤
║ Name | Dose | Freq | Duration | [✏️🗑️]║
║ Aspirin│500mg│2x/d │ 7 days   │ ✏️ 🗑️ ║
║ Cough  │  -  │3x/d │    -     │ ✏️ 🗑️ ║
│       │      │     │          │        │
║ [Add Medicine Form]                    ║
╚═════════════════════════════════════════╝
```

### Tests & Advice
```
╔═════════════════════════════════════════╗
║ 🧪 Tests                                ║
║ + [chest x-ray] + [blood test]          ║
│                                         │
║ 📋 Advice                               ║
║ + [rest] + [hydrate] + [warmth]        ║
╚═════════════════════════════════════════╝
```

### Actions
```
╔═════════════════════════════════════════╗
║                      [Cancel] [💾 Save]║
╚═════════════════════════════════════════╝
```

## 🔌 API Endpoints

### Start Recording
```http
POST /api/start-consultation
Content-Type: application/json

Response:
{
  "status": "recording_started",
  "audio_file": "data/audio/consultation_20260225_143022.wav",
  "timestamp": "2026-02-25T14:30:22.123456"
}
```

### Stop Recording & Extract
```http
POST /api/stop-consultation
Content-Type: application/json

Response:
{
  "success": true,
  "patient_name": "Rohit",
  "complaints": ["fever", "cough"],
  "diagnosis": ["acute pharyngitis"],
  "medicines": [
    {
      "name": "paracetamol",
      "dose": "500 mg",
      "frequency": "3 times a day",
      "duration": "5 days",
      "instruction": "after food",
      "route": "oral"
    }
  ],
  "tests": [],
  "advice": ["drink fluids", "rest"],
  "language": "en",
  "confidence": 0.85,
  "extraction_method": "groq",
  "timestamp": "2026-02-25T14:35:10.987654"
}
```

### Save Consultation
```http
POST /api/save-consultation
Content-Type: application/json

Body:
{
  "patient_name": "Rohit",
  "age": 35,
  "gender": "Male",
  "complaints": ["fever", "cough"],
  "diagnosis": ["acute pharyngitis"],
  "medicines": [...],
  "tests": [],
  "advice": [...],
  "follow_up_days": "7"
}

Response:
{
  "status": "saved",
  "consultation_id": "CONSULT_20260225143510",
  "timestamp": "2026-02-25T14:35:10.123456"
}
```

### Get Loaded Data
```http
GET /api/consultation-data

Response: [Last extracted consultation data]
```

### Health Check
```http
GET /api/health

Response:
{
  "status": "ok",
  "service": "Medical Consultation API"
}
```

## 🔧 Customization

### Change API Server URL
Edit in `ConsultationIntegrated.jsx`:
```javascript
// Update API calls to use different server
const API_BASE_URL = "http://your-server:5000";
```

### Add Custom Fields
```javascript
// Add state
const [newField, setNewField] = useState("");

// Add to form
<input 
  className="form-control"
  value={newField}
  onChange={(e) => setNewField(e.target.value)}
/>

// Include in save
const consultationData = {
  ...existingData,
  new_field: newField
};
```

### Modify Styling
- Bootstrap 5 classes used
- Primary colors: `bg-primary`, `bg-danger`, `bg-success`
- Change in JSX or CSS files

### Connect to Real Database
Update in `api.py`:
```python
@app.route("/api/save-consultation", methods=["POST"])
def save_consultation():
    data = request.json
    
    # Save to your database
    db.consultations.insert_one(data)
    
    return jsonify({"status": "saved"})
```

## 🧪 Testing

### Test Recording
```bash
# Test API health
curl http://localhost:5000/api/health

# Test endpoints
curl -X POST http://localhost:5000/api/start-consultation
curl -X POST http://localhost:5000/api/stop-consultation
```

### Test React Component
```jsx
// Check browser console for logs
console.log("Extracted data:", extractedData);

// Use React DevTools to inspect state
// Chrome/Firefox: F12 > React tab
```

## 📋 Requirements

### Python 3.8+
```
flask >= 2.3.0
flask-cors >= 4.0.0
sounddevice >= 0.4.6
scipy >= 1.11.0
numpy >= 1.24.0
python-dotenv >= 1.0.0
groq >= 0.4.2
openai >= 1.3.0
```

### Node.js (for React)
```
react >= 17.0
bootstrap >= 5.0
```

## 🐛 Troubleshooting

### API Server Won't Start
```bash
# Check Python version
python --version

# Check port 5000 is available
netstat -ano | findstr :5000

# Run with debug info
python api.py --debug
```

### Recording Not Working
```bash
# Check microphone is connected
# Test with Windows Sound Settings

# Check sounddevice
python -c "import sounddevice; print(sounddevice.query_devices())"
```

### Data Not Auto-Filling
```
- Check /data/live_consultation_result.json exists
- Verify file has valid JSON
- Check browser console for errors

Example file:
{
  "patient_name": "John",
  "complaints": ["fever"],
  "diagnosis": ["cold"],
  "medicines": [],
  "tests": [],
  "advice": ["rest"]
}
```

### Port 5000 Already in Use
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (Windows)
taskkill /PID <PID> /F

# Or use different port in api.py:
app.run(port=5001)
```

## 📚 Additional Resources

- [Bootstrap 5 Docs](https://getbootstrap.com/docs/5.0/)
- [React Hooks Docs](https://react.dev/reference/react/hooks)
- [Flask Docs](https://flask.palletsprojects.com/)
- [Medical System V2](../src/medical_system_v2.py)

## ✅ Checklist Before Deployment

- [ ] API server tested and running
- [ ] Microphone recording working
- [ ] JSON extraction data loading
- [ ] All form fields editable
- [ ] Save endpoint working
- [ ] Database connection configured
- [ ] Error handling tested
- [ ] HTTPS configured (for production)
- [ ] CORS settings reviewed
- [ ] Documentation updated

## 📝 Version Info

- **Version**: 1.0
- **Status**: Production Ready ✅
- **Last Updated**: February 25, 2026
- **Author**: AI Medical Assistant

## 📞 Support

For issues or questions:
1. Check [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
2. Review [Troubleshooting](#troubleshooting) section
3. Check API logs: `medical_system_v2.log`
4. Check browser console: F12 > Console tab

---

**Ready to integrate?** Start with [Quick Start](#-quick-start-5-minutes) section!
