import React, { useState } from "react";
import InputTextField from "../../../Components/Interfaces/InputTextField";
import FormActionButtons from "../../../Components/Interfaces/FormActionButtons";
import StatusModal from "../../../Components/StatusModal/SuccessStatus";

const ConsultationDetails = () => {
  const [durationUnit, setDurationUnit] = useState("days");
  const [durationValue, setDurationValue] = useState("");
  const [severity, setSeverity] = useState("");
  const [open, setOpen] = useState(false);

  const [complaint, setComplaint] = useState("");
  const [notes, setNotes] = useState("");
  const [history, setHistory] = useState("");
  const [diagnosis, setDiagnosis] = useState("");

  const units = ["hours", "days", "weeks", "months"];

  // 🔹 Reset all fields
  const resetForm = () => {
    setComplaint("");
    setDurationValue("");
    setDurationUnit("days");
    setSeverity("");
    setNotes("");
    setHistory("");
    setDiagnosis("");
  };

  const handleSubmit = () => {
    console.log("Consultation Details:", {
      complaint,
      duration: `${durationValue} ${durationUnit}`,
      severity,
      notes,
      medicalHistory: history,
      diagnosis,
    });

    setOpen(true);
    resetForm(); // ✅ clear form after save
  };

  return (
    <div className="row g-3">

      {/* Chief Complaint */}
      <div className="col-md-6">
        <InputTextField
          label="Chief Complaint"
          className="bg-w"
          placeholder="Enter here"
          required
          value={complaint}
          onChange={(e) => setComplaint(e.target.value)}
        />
      </div>

      {/* Duration */}
      <div className="col-md-6">
        <label className="form-label fw-b">
          Duration <span className="text-danger">*</span>
        </label>

        <div className="d-flex gap-2 align-items-center flex-wrap">
          <input
            className="form-control"
            style={{maxWidth:"70px"}}
            placeholder="00"
            value={durationValue}
            onChange={(e) => setDurationValue(e.target.value)}
          />

          {units.map((unit) => (
            <button
              key={unit}
              type="button"
              className={`btn btn-sm px-3 py-2 ${
                durationUnit === unit ? "c-dg bg-w bor-dg" : "bg-gy2"
              }`}
              onClick={() => setDurationUnit(unit)}
            >
              {unit.charAt(0).toUpperCase() + unit.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Severity */}
      <div className="col-md-6">
        <label className="form-label fw-b">Severity</label>
        <div className="d-flex gap-4 mt-1">
          {["Mild", "Moderate", "Severe"].map((level) => (
            <div className="form-check" key={level}>
              <input
                type="radio"
                id={level}
                name="severity"
                className="form-check-input"
                checked={severity === level}
                onChange={() => setSeverity(level)}
              />
              <label htmlFor={level} className="form-check-label">
                {level}
              </label>
            </div>
          ))}
        </div>
      </div>

      {/* Additional Notes */}
      <div className="col-md-6">
        <InputTextField
          label="Additional Notes"
          placeholder="Enter here"
          className="bg-w"
          multiline
          rows={1}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
      </div>

      {/* Medical History */}
      <div className="col-md-6">
        <InputTextField
          label="Medical History"
          placeholder="Enter here"
          className="bg-w"
          value={history}
          onChange={(e) => setHistory(e.target.value)}
        />
      </div>

      {/* Diagnosis */}
      <div className="col-md-6">
        <InputTextField
          label="Diagnosis"
          placeholder="Enter here"
          required
          className="bg-w"
          value={diagnosis}
          onChange={(e) => setDiagnosis(e.target.value)}
        />
      </div>

      {/* Actions */}
      <div className="col-12 d-flex justify-content-end gap-2 mt-3">
        <FormActionButtons
          onCancel={resetForm} // optional: clear on cancel
          onSubmit={handleSubmit}
          cancelLabel="Cancel"
          submitLabel="Save & Next"
        />
      </div>

      {/* Status Modal */}
      <StatusModal
        open={open}
        title="You have successfully started the consultation."
        onClose={() => setOpen(false)}
        buttonText="Go to Consultation"
      />
    </div>
  );
};

export default ConsultationDetails;
