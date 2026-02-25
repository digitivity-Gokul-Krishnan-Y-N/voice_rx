# Consultation Integration Guide

## 🎯 Overview

The **ConsultationIntegrated** component is a single-page React component that:
- ✅ Records voice input with **Start/Stop buttons**
- ✅ Auto-fills from extracted medical data (JSON)
- ✅ Allows **inline editing** of all fields
- ✅ Manages medicines, tests, advice, and follow-ups **on the same page**
- ✅ No extra pages needed

## 📁 File Structure

```
consultation_pages/
├── Consultation.jsx                    # Main entry point (updated)
├── ConsultationIntegrated.jsx          # ✨ NEW: Integrated component
├── api.py                              # ✨ NEW: Flask API backend
├── ConsultationDetails/
├── ConsultationMedicines/
├── ConsultationTests/
└── ConsultationFollowUp/               # Old components (kept for reference)
```

## 🚀 Quick Start

### 1. **Replace Old Consultation Component**
The updated `Consultation.jsx` now uses `ConsultationIntegrated.jsx` instead of multiple tab-based components.

### 2. **Start the Backend API**

```bash
# Install Flask dependencies
pip install flask flask-cors

# Run the API server
cd d:\voice_rx\consultation_pages
python api.py
```

API runs on: `http://localhost:5000`

### 3. **Use in Your React App**

```jsx
import Consultation from "./consultation_pages/Consultation";

function App() {
  return <Consultation />;
}
```

## 🎤 Features

### Voice Recording
- Click **🔴 Start Recording** to begin
- Click **⏹️ Stop Recording** to finish
- Audio is automatically processed and data is extracted

```javascript
const handleStartRecording = async () => {
  const response = await fetch("/api/start-consultation", { method: "POST" });
  // Recording begins...
};

const handleStopRecording = async () => {
  const response = await fetch("/api/stop-consultation", { method: "POST" });
  // Audio is processed and fields are auto-filled
};
```

### Auto-Fill from Extracted Data
JSON data from medical system automatically populates:
- Patient name
- Complaints
- Diagnosis
- Medicines
- Tests
- Advice

Source: `/data/live_consultation_result.json`

```javascript
const loadExtractedData = async () => {
  const response = await fetch("/data/live_consultation_result.json");
  const data = await response.json();
  
  // Auto-fill fields
  setPatientName(data.patient_name);
  setComplaints(data.complaints);
  setMedicines(data.medicines);
  setAdvice(data.advice);
};
```

### Inline Editing
All fields are fully editable:

**Complaints & Diagnosis:**
- Add with input field + button
- Remove with close button (❌)

**Medicines:**
- Edit table with full details (name, dose, frequency, duration)
- Update or delete medicines inline
- No modal dialogs needed

**Tests:**
- Add lab, imaging, or home tests
- Quick removal

**Advice & Follow-up:**
- Add multiple pieces of advice
- Set follow-up days
- All on same page

## 📋 API Endpoints

### Start Recording
```
POST /api/start-consultation
Response: { status: "recording_started", audio_file, timestamp }
```

### Stop Recording & Extract
```
POST /api/stop-consultation
Response: { success, patient_name, complaints, diagnosis, medicines, tests, advice, ... }
```

### Save Consultation
```
POST /api/save-consultation
Body: { patient_name, age, gender, complaints, diagnosis, medicines, tests, advice, follow_up_days }
Response: { status: "saved", consultation_id, timestamp }
```

### Get Consultation Data
```
GET /api/consultation-data
Response: { last extracted consultation result }
```

### Health Check
```
GET /api/health
Response: { status: "ok" }
```

## 🔄 Data Flow

```
┌─────────────────────────────────────────┐
│ 1. User clicks "Start Recording" 🔴     │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ 2. API records audio (microphone)       │
│    /api/start-consultation              │
└────────────┬────────────────────────────┘
             │
    [User speaks to microphone]
             │
             ▼
┌─────────────────────────────────────────┐
│ 3. User clicks "Stop Recording" ⏹️      │
│    /api/stop-consultation               │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ 4. Backend processes with medical_system│
│    - Transcription (Whisper)            │
│    - Extraction (Groq/Rules)            │
│    - Validation                         │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ 5. React component auto-fills all fields│
│    from extracted data                  │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ 6. User reviews & edits (if needed)     │
│    - All fields are editable            │
│    - No extra pages                     │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ 7. User clicks "Save Consultation"      │
│    /api/save-consultation               │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ 8. Consultation saved to database ✅    │
└─────────────────────────────────────────┘
```

## 🎨 UI Sections

### 1. Recording Controls
```
┌─────────────────────────────────────────┐
│ 🎤 Voice Consultation  [Start] [Stop]   │
└─────────────────────────────────────────┘
```

### 2. Patient Info
```
┌─────────────────────────────────────────┐
│ 👤 Patient Information                  │
│ Name: [____________]  Age: [___]        │
│                       Gender: [Select]  │
└─────────────────────────────────────────┘
```

### 3. Complaints & Diagnosis (Side by Side)
```
┌──────────────────┬──────────────────┐
│ 🤒 Complaints    │ ⚕️ Diagnosis     │
│ + throat pain    │ + pharyngitis    │
│ + cough          │ + infection      │
└──────────────────┴──────────────────┘
```

### 4. Medicines Table
```
┌─────────────────────────────────────────┐
│ 💊 Medicines                            │
├─────────────────────────────────────────┤
│ Medicine │ Dose  │ Freq  │ Duration │ ✏️ │
│ Aspirin  │ 500mg │ 2x/d  │ 7 days   │ 🗑️ │
│ Cough    │ -     │ 3x/d  │ -        │ ✏️ │
└─────────────────────────────────────────┘
```

### 5. Tests & Advice
```
┌─────────────────────────────────────────┐
│ 🧪 Tests  + chest x-ray  + blood test   │
│ 📋 Advice + rest  + hydrate  + warmth   │
└─────────────────────────────────────────┘
```

### 6. Save Button
```
┌─────────────────────────────────────────┐
│ [Cancel]  [💾 Save Consultation]        │
└─────────────────────────────────────────┘
```

## 🔧 Customization

### Change API URL
```javascript
// In ConsultationIntegrated.jsx, update:
const API_URL = "http://your-api-url:5000";

// Then use:
fetch(`${API_URL}/api/start-consultation`, ...)
```

### Modify Fields
```javascript
// Add new field to state:
const [newField, setNewField] = useState("");

// Add to form:
<input
  className="form-control"
  value={newField}
  onChange={(e) => setNewField(e.target.value)}
/>
```

### Change Styling
Bootstrap classes are used. Modify:
- `bg-primary` → Card header colors
- `btn-success` → Button colors
- `badge` → Tag/chip styling

## ✅ Requirements Met

- ✅ **Single page** - No extra pages created
- ✅ **Start/Stop buttons** - Record voice input
- ✅ **Auto-fill** - JSON data populates all fields
- ✅ **Inline editing** - Edit medicines, advice, tests on same page
- ✅ **All sections together** - Complaints, medicines, tests, advice all visible

## 🐛 Troubleshooting

### Recording not working
```
Check: /api/health endpoint
python api.py --debug
```

### Data not loading
```
Check: /data/live_consultation_result.json exists
Verify path in loadExtractedData()
```

### Editing not saving
```
Ensure state updates in React DevTools
Check browser console for errors
```

## 📚 Example Usage

```jsx
import Consultation from "./consultation_pages/Consultation";

export default function ConsultationPage() {
  return (
    <div>
      <Consultation />
    </div>
  );
}
```

## 📞 Support

For issues or customization, check:
- React component props in `ConsultationIntegrated.jsx`
- API routes in `api.py`
- Medical system extraction in `medical_system_v2.py`

---

**Version**: 1.0  
**Last Updated**: February 2026  
**Status**: ✅ Production Ready
