import React, { useState, useEffect } from "react";
import "bootstrap/dist/css/bootstrap.min.css";

const ConsultationIntegrated = () => {
  // ==================== STATE MANAGEMENT ====================
  const [isRecording, setIsRecording] = useState(false);
  const [extractedData, setExtractedData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Consultation Details
  const [patientName, setPatientName] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("Male");
  const [complaints, setComplaints] = useState([]);
  const [newComplaint, setNewComplaint] = useState("");
  const [diagnosis, setDiagnosis] = useState([]);
  const [newDiagnosis, setNewDiagnosis] = useState("");

  // Medicines
  const [medicines, setMedicines] = useState([]);
  const [editingMedIndex, setEditingMedIndex] = useState(null);
  const [editingMed, setEditingMed] = useState({
    name: "",
    dose: "",
    frequency: "",
    duration: "",
    instruction: "",
    route: "oral",
  });

  // Tests
  const [tests, setTests] = useState([]);
  const [newTestName, setNewTestName] = useState("");
  const [newTestType, setNewTestType] = useState("lab");

  // Follow-up & Advice
  const [advice, setAdvice] = useState([]);
  const [newAdvice, setNewAdvice] = useState("");
  const [followUpDays, setFollowUpDays] = useState("7");

  // ==================== LOAD EXTRACTED DATA ====================
  useEffect(() => {
    loadExtractedData();
  }, []);

  const loadExtractedData = async () => {
    try {
      const response = await fetch("/data/live_consultation_result.json");
      if (!response.ok) throw new Error("Failed to load data");

      const data = await response.json();
      setExtractedData(data);

      // Auto-fill all fields from extracted data
      if (data.patient_name) setPatientName(data.patient_name);
      if (data.complaints?.length > 0) setComplaints(data.complaints);
      if (data.diagnosis?.length > 0) setDiagnosis(data.diagnosis);
      if (data.medicines?.length > 0) setMedicines(data.medicines);
      if (data.tests?.length > 0) setTests(data.tests);
      if (data.advice?.length > 0) setAdvice(data.advice);
    } catch (error) {
      console.error("Error loading extracted data:", error);
    }
  };

  // ==================== RECORDING HANDLERS ====================
  const handleStartRecording = async () => {
    try {
      setIsRecording(true);
      setLoading(true);

      // Call backend to start recording and process audio
      const response = await fetch("/api/start-consultation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      if (!response.ok) throw new Error("Failed to start recording");

      // Reload extracted data after processing
      setTimeout(() => {
        loadExtractedData();
        setLoading(false);
      }, 2000);
    } catch (error) {
      console.error("Recording error:", error);
      setIsRecording(false);
      setLoading(false);
    }
  };

  const handleStopRecording = async () => {
    try {
      setIsRecording(false);
      setLoading(true);

      // Call backend to stop recording and extract data
      const response = await fetch("/api/stop-consultation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      if (!response.ok) throw new Error("Failed to stop recording");

      const result = await response.json();

      // Auto-fill extracted data
      if (result.success) {
        setExtractedData(result);
        if (result.patient_name) setPatientName(result.patient_name);
        if (result.complaints?.length) setComplaints(result.complaints);
        if (result.diagnosis?.length) setDiagnosis(result.diagnosis);
        if (result.medicines?.length) setMedicines(result.medicines);
        if (result.tests?.length) setTests(result.tests);
        if (result.advice?.length) setAdvice(result.advice);
      }

      setLoading(false);
    } catch (error) {
      console.error("Stop recording error:", error);
      setLoading(false);
    }
  };

  // ==================== COMPLAINT HANDLERS ====================
  const addComplaint = () => {
    if (newComplaint.trim()) {
      setComplaints([...complaints, newComplaint.trim()]);
      setNewComplaint("");
    }
  };

  const removeComplaint = (index) => {
    setComplaints(complaints.filter((_, i) => i !== index));
  };

  // ==================== DIAGNOSIS HANDLERS ====================
  const addDiagnosis = () => {
    if (newDiagnosis.trim()) {
      setDiagnosis([...diagnosis, newDiagnosis.trim()]);
      setNewDiagnosis("");
    }
  };

  const removeDiagnosis = (index) => {
    setDiagnosis(diagnosis.filter((_, i) => i !== index));
  };

  // ==================== MEDICINE HANDLERS ====================
  const addMedicine = () => {
    if (editingMed.name.trim()) {
      if (editingMedIndex !== null) {
        // Update existing
        const updated = [...medicines];
        updated[editingMedIndex] = editingMed;
        setMedicines(updated);
        setEditingMedIndex(null);
      } else {
        // Add new
        setMedicines([...medicines, editingMed]);
      }
      setEditingMed({
        name: "",
        dose: "",
        frequency: "",
        duration: "",
        instruction: "",
        route: "oral",
      });
    }
  };

  const editMedicine = (index) => {
    setEditingMed(medicines[index]);
    setEditingMedIndex(index);
  };

  const removeMedicine = (index) => {
    setMedicines(medicines.filter((_, i) => i !== index));
  };

  // ==================== TEST HANDLERS ====================
  const addTest = () => {
    if (newTestName.trim()) {
      setTests([...tests, { name: newTestName.trim(), type: newTestType }]);
      setNewTestName("");
    }
  };

  const removeTest = (index) => {
    setTests(tests.filter((_, i) => i !== index));
  };

  // ==================== ADVICE HANDLERS ====================
  const addAdvice = () => {
    if (newAdvice.trim()) {
      setAdvice([...advice, newAdvice.trim()]);
      setNewAdvice("");
    }
  };

  const removeAdvice = (index) => {
    setAdvice(advice.filter((_, i) => i !== index));
  };

  // ==================== SAVE CONSULTATION ====================
  const saveConsultation = async () => {
    const consultationData = {
      patient_name: patientName,
      age: age,
      gender: gender,
      complaints: complaints,
      diagnosis: diagnosis,
      medicines: medicines,
      tests: tests,
      advice: advice,
      follow_up_days: followUpDays,
      timestamp: new Date().toISOString(),
    };

    try {
      const response = await fetch("/api/save-consultation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(consultationData),
      });

      if (!response.ok) throw new Error("Failed to save consultation");

      alert("✅ Consultation saved successfully!");
    } catch (error) {
      console.error("Save error:", error);
      alert("❌ Failed to save consultation");
    }
  };

  // ==================== RENDER ====================
  return (
    <div className="container-fluid mt-4">
      {/* ==================== RECORDING CONTROLS ==================== */}
      <div className="card shadow-sm mb-4 border-0">
        <div className="card-header bg-dark text-white d-flex justify-content-between align-items-center">
          <h5 className="mb-0">🎤 Voice Consultation</h5>
          <div className="d-flex gap-2">
            {!isRecording ? (
              <button
                className="btn btn-success btn-lg"
                onClick={handleStartRecording}
                disabled={loading}
              >
                {loading ? "Processing..." : "🔴 Start Recording"}
              </button>
            ) : (
              <button
                className="btn btn-danger btn-lg"
                onClick={handleStopRecording}
                disabled={loading}
              >
                {loading ? "Processing..." : "⏹️ Stop Recording"}
              </button>
            )}
          </div>
        </div>
        {isRecording && (
          <div className="card-body bg-light">
            <div className="alert alert-warning mb-0">
              <strong>🎙️ Recording in progress...</strong> Speak clearly for better
              extraction.
            </div>
          </div>
        )}
      </div>

      {loading && (
        <div className="alert alert-info" role="alert">
          ⏳ Processing audio and extracting data... Please wait.
        </div>
      )}

      {/* ==================== PATIENT INFO ==================== */}
      <div className="card shadow-sm mb-4">
        <div className="card-header bg-primary text-white">
          <h5 className="mb-0">👤 Patient Information</h5>
        </div>
        <div className="card-body">
          <div className="row g-3">
            <div className="col-md-6">
              <label className="form-label fw-bold">Patient Name</label>
              <input
                type="text"
                className="form-control"
                placeholder="Auto-filled from voice"
                value={patientName}
                onChange={(e) => setPatientName(e.target.value)}
              />
            </div>
            <div className="col-md-3">
              <label className="form-label fw-bold">Age</label>
              <input
                type="number"
                className="form-control"
                placeholder="Enter age"
                value={age}
                onChange={(e) => setAge(e.target.value)}
              />
            </div>
            <div className="col-md-3">
              <label className="form-label fw-bold">Gender</label>
              <select
                className="form-select"
                value={gender}
                onChange={(e) => setGender(e.target.value)}
              >
                <option>Male</option>
                <option>Female</option>
                <option>Other</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* ==================== COMPLAINTS & DIAGNOSIS ==================== */}
      <div className="row g-4 mb-4">
        {/* Complaints */}
        <div className="col-lg-6">
          <div className="card shadow-sm">
            <div className="card-header bg-info text-white">
              <h5 className="mb-0">🤒 Chief Complaints</h5>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <div className="input-group">
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Add complaint..."
                    value={newComplaint}
                    onChange={(e) => setNewComplaint(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && addComplaint()}
                  />
                  <button
                    className="btn btn-info"
                    onClick={addComplaint}
                    type="button"
                  >
                    +
                  </button>
                </div>
              </div>

              <div className="d-flex flex-wrap gap-2">
                {complaints.map((complaint, idx) => (
                  <div
                    key={idx}
                    className="badge bg-info d-flex align-items-center gap-2 p-2"
                  >
                    {complaint}
                    <button
                      className="btn-close btn-close-white"
                      onClick={() => removeComplaint(idx)}
                      type="button"
                      style={{ marginLeft: "5px" }}
                    />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Diagnosis */}
        <div className="col-lg-6">
          <div className="card shadow-sm">
            <div className="card-header bg-warning text-dark">
              <h5 className="mb-0">⚕️ Diagnosis</h5>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <div className="input-group">
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Add diagnosis..."
                    value={newDiagnosis}
                    onChange={(e) => setNewDiagnosis(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && addDiagnosis()}
                  />
                  <button
                    className="btn btn-warning"
                    onClick={addDiagnosis}
                    type="button"
                  >
                    +
                  </button>
                </div>
              </div>

              <div className="d-flex flex-wrap gap-2">
                {diagnosis.map((diag, idx) => (
                  <div key={idx} className="badge bg-warning p-2 d-flex align-items-center gap-2">
                    {diag}
                    <button
                      className="btn-close"
                      onClick={() => removeDiagnosis(idx)}
                      type="button"
                      style={{ marginLeft: "5px" }}
                    />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ==================== MEDICINES ==================== */}
      <div className="card shadow-sm mb-4">
        <div className="card-header bg-danger text-white">
          <h5 className="mb-0">💊 Medicines</h5>
        </div>
        <div className="card-body">
          {/* Medicine Form */}
          <div className="row g-3 mb-4 p-3 bg-light rounded">
            <div className="col-md-3">
              <input
                type="text"
                className="form-control"
                placeholder="Medicine name"
                value={editingMed.name}
                onChange={(e) =>
                  setEditingMed({ ...editingMed, name: e.target.value })
                }
              />
            </div>
            <div className="col-md-2">
              <input
                type="text"
                className="form-control"
                placeholder="Dose (mg)"
                value={editingMed.dose}
                onChange={(e) =>
                  setEditingMed({ ...editingMed, dose: e.target.value })
                }
              />
            </div>
            <div className="col-md-2">
              <input
                type="text"
                className="form-control"
                placeholder="Frequency"
                value={editingMed.frequency}
                onChange={(e) =>
                  setEditingMed({ ...editingMed, frequency: e.target.value })
                }
              />
            </div>
            <div className="col-md-2">
              <input
                type="text"
                className="form-control"
                placeholder="Duration"
                value={editingMed.duration}
                onChange={(e) =>
                  setEditingMed({ ...editingMed, duration: e.target.value })
                }
              />
            </div>
            <div className="col-md-3">
              <button
                className="btn btn-danger w-100"
                onClick={addMedicine}
                type="button"
              >
                {editingMedIndex !== null ? "✏️ Update" : "➕ Add"}
              </button>
            </div>
          </div>

          {/* Medicines List */}
          <div className="table-responsive">
            <table className="table table-sm table-hover">
              <thead className="table-light">
                <tr>
                  <th>Medicine</th>
                  <th>Dose</th>
                  <th>Frequency</th>
                  <th>Duration</th>
                  <th>Instructions</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {medicines.map((med, idx) => (
                  <tr key={idx}>
                    <td className="fw-bold">{med.name}</td>
                    <td>{med.dose || "-"}</td>
                    <td>{med.frequency || "-"}</td>
                    <td>{med.duration || "-"}</td>
                    <td>{med.instruction || "-"}</td>
                    <td>
                      <button
                        className="btn btn-sm btn-warning"
                        onClick={() => editMedicine(idx)}
                      >
                        ✏️
                      </button>
                      <button
                        className="btn btn-sm btn-danger ms-1"
                        onClick={() => removeMedicine(idx)}
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* ==================== TESTS ==================== */}
      <div className="card shadow-sm mb-4">
        <div className="card-header bg-success text-white">
          <h5 className="mb-0">🧪 Tests</h5>
        </div>
        <div className="card-body">
          <div className="row g-3 mb-3">
            <div className="col-md-8">
              <input
                type="text"
                className="form-control"
                placeholder="Test name (e.g., Blood Test, CT Scan)"
                value={newTestName}
                onChange={(e) => setNewTestName(e.target.value)}
              />
            </div>
            <div className="col-md-2">
              <select
                className="form-select"
                value={newTestType}
                onChange={(e) => setNewTestType(e.target.value)}
              >
                <option value="lab">Lab</option>
                <option value="imaging">Imaging</option>
                <option value="home">Home</option>
              </select>
            </div>
            <div className="col-md-2">
              <button
                className="btn btn-success w-100"
                onClick={addTest}
                type="button"
              >
                ➕ Add
              </button>
            </div>
          </div>

          <div className="d-flex flex-wrap gap-2">
            {tests.map((test, idx) => (
              <div key={idx} className="badge bg-success d-flex align-items-center gap-2 p-2">
                {test.name} ({test.type})
                <button
                  className="btn-close btn-close-white"
                  onClick={() => removeTest(idx)}
                  type="button"
                  style={{ marginLeft: "5px" }}
                />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ==================== ADVICE & FOLLOW-UP ==================== */}
      <div className="card shadow-sm mb-4">
        <div className="card-header" style={{ backgroundColor: "#6f42c1" }}>
          <h5 className="mb-0 text-white">📋 Advice & Follow-up</h5>
        </div>
        <div className="card-body">
          <div className="row g-3 mb-4">
            <div className="col-md-8">
              <input
                type="text"
                className="form-control"
                placeholder="Add advice (e.g., rest, drink fluids)"
                value={newAdvice}
                onChange={(e) => setNewAdvice(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && addAdvice()}
              />
            </div>
            <div className="col-md-4">
              <button className="btn btn-purple w-100" onClick={addAdvice} type="button">
                ➕ Add Advice
              </button>
            </div>
          </div>

          <div className="d-flex flex-wrap gap-2 mb-4">
            {advice.map((adv, idx) => (
              <div key={idx} className="badge p-2 d-flex align-items-center gap-2" style={{ backgroundColor: "#6f42c1", color: "white" }}>
                {adv}
                <button
                  className="btn-close btn-close-white"
                  onClick={() => removeAdvice(idx)}
                  type="button"
                  style={{ marginLeft: "5px" }}
                />
              </div>
            ))}
          </div>

          <div className="row g-3">
            <div className="col-md-4">
              <label className="form-label fw-bold">Follow-up after (days)</label>
              <input
                type="number"
                className="form-control"
                value={followUpDays}
                onChange={(e) => setFollowUpDays(e.target.value)}
              />
            </div>
          </div>
        </div>
      </div>

      {/* ==================== ACTION BUTTONS ==================== */}
      <div className="d-flex gap-3 mb-5 justify-content-end">
        <button
          className="btn btn-secondary btn-lg"
          onClick={() => window.location.reload()}
        >
          Cancel
        </button>
        <button
          className="btn btn-primary btn-lg"
          onClick={saveConsultation}
        >
          💾 Save Consultation
        </button>
      </div>
    </div>
  );
};

export default ConsultationIntegrated;
