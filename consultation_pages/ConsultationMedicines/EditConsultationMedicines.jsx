import React, { useState } from "react";
import InputTextField from "../../../Components/Interfaces/InputTextField";
import FormActionButtons from "../../../Components/Interfaces/FormActionButtons";
import StatusModal from "../../../Components/StatusModal/SuccessStatus";
import DropdownField from "../../../Components/Interfaces/DropdownField";
import AddMoreDropdown from "../../../Components/Interfaces/AddMoreDropdown";
import ConsultationMedList from "./ConsultationMedList";

const ConsultationMedicines = () => {
  const [durationUnit, setDurationUnit] = useState("Days");
  const [durationValue, setDurationValue] = useState("");
  const [instructions, setInstructions] = useState([]);
  const [timing, setTiming] = useState("");
  const [frequency, setFrequency] = useState("");
  const [weeklyOption, setWeeklyOption] = useState("");
  const [medicine, setMedicine] = useState("");
  const [dosage, setDosage] = useState("");
  const [notes, setNotes] = useState("");

  const [list, setList] = useState(false);
  const [openModal, setOpenModal] = useState(false);
  const [openStatus, setOpenStatus] = useState(false);

  const units = ["Days", "Weeks", "Until Next Consultation"];

  // 🔹 Instructions toggle
  const handleInstructionChange = (value) => {
    setInstructions((prev) =>
      prev.includes(value)
        ? prev.filter((item) => item !== value)
        : [...prev, value]
    );
  };

  // 🔹 Reset form
  const resetForm = () => {
    setMedicine("");
    setDosage("");
    setInstructions([]);
    setTiming("");
    setFrequency("");
    setWeeklyOption("");
    setDurationValue("");
    setDurationUnit("Days");
    setNotes("");
  };

  // 🔹 Collect data
  const getPayload = () => ({
    medicine,
    dosage,
    instructions,
    timing,
    frequency: frequency === "weekly" ? `${frequency} - ${weeklyOption}` : frequency,
    duration: `${durationValue} ${durationUnit}`,
    notes,
  });

  // 🔹 Save → go to list
  const handleSave = () => {
    console.log("Medicine Saved:", getPayload());
    setList(true);
  };

  // 🔹 Save & Add Next
  const handleSaveNext = () => {
    console.log("Medicine Saved (Next):", getPayload());
    resetForm();
    setOpenStatus(true);
  };

  if (list) {
    return <ConsultationMedList onCancel={() => setList(false)} />;
  }

  return (
    <div className="row g-3">

      {/* Skip */}
      <div className="col-12 d-flex justify-content-end">
        <a
          href="#"
          className="c-dg"
          onClick={(e) => {
            e.preventDefault();
            resetForm();
          }}
        >
          Skip
        </a>
      </div>

      {/* Medicine */}
      <div className="col-md-6">
        <AddMoreDropdown
          label="Select Medicine"
          value={medicine}
          options={[
            { value: "med1", label: "Medicine 1" },
            { value: "med2", label: "Medicine 2" },
          ]}
          onChange={(e) => setMedicine(e.target.value)}
          onAddMore={() => setOpenModal(true)}
          placeholder="Search medicine"
          required
        />
      </div>

      {/* Dosage */}
      <div className="col-md-6">
        <DropdownField
          label="Dosage"
          value={dosage}
          onChange={(e) => setDosage(e.target.value)}
          options={[
            { value: "once", label: "Once a day" },
            { value: "twice", label: "Twice a day" },
            { value: "thrice", label: "Thrice a day" },
          ]}
          placeholder="Select dosage"
          required
        />
      </div>

      {/* Instructions */}
      <div className="col-md-6">
        <label className="form-label fw-b">Instructions</label>
        <div className="border rounded-3 bg-white p-3">
          <div className="d-flex gap-4 flex-wrap">
            {["Morning", "Afternoon", "Evening"].map((item) => (
              <div className="form-check" key={item}>
                <input
                  type="checkbox"
                  className="form-check-input"
                  checked={instructions.includes(item)}
                  onChange={() => handleInstructionChange(item)}
                />
                <label className="form-check-label ms-1">{item}</label>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Timing */}
      <div className="col-md-6">
        <label className="form-label fw-b">Timings</label>
        <div className="d-flex gap-4 mt-1">
          {["Before Food", "After Food"].map((item) => (
            <div className="form-check" key={item}>
              <input
                type="radio"
                className="form-check-input"
                checked={timing === item}
                onChange={() => setTiming(item)}
              />
              <label className="form-check-label">{item}</label>
            </div>
          ))}
        </div>
      </div>

      {/* Frequency */}
      <div className="col-md-6">
        <DropdownField
          label="Frequency"
          value={frequency}
          onChange={(e) => {
            setFrequency(e.target.value);
            setWeeklyOption("");
          }}
          options={[
            { value: "daily", label: "Daily" },
            { value: "weekly", label: "Weekly" },
            { value: "as needed", label: "As Needed" },
          ]}
          required
        />

          {frequency === "weekly" && (
          <div className="mt-2 ps-1 bg-w p-3 rounded-2 bor-dg">
            <div className="d-flex flex-wrap gap-3">
              {[
                "Once",
                "Twice",
                "Thrice",
                "Alternate Week",
                "Every Three Weeks",
              ].map((option) => (
                <div className="form-check" key={option}>
                  <input
                    type="radio"
                    className="form-check-input"
                    checked={weeklyOption === option}
                    onChange={() => setWeeklyOption(option)}
                  />
                  <label className="form-check-label">{option}</label>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Duration */}
      <div className="col-md-6">
        <label className="form-label fw-b">Duration</label>
        <div className="d-flex gap-3 align-items-center">
          <input
            className="form-control"
            style={{ width: 70 }}
            placeholder="00"
            value={durationValue}
            onChange={(e) => setDurationValue(e.target.value)}
          />

          {units.map((unit) => (
            <button
              key={unit}
              type="button"
              className={`btn btn-sm py-2 px-3 ${
                durationUnit === unit ? "c-dg bg-w bor-dg" : "bg-gy2"
              }`}
              onClick={() => setDurationUnit(unit)}
            >
              {unit}
            </button>
          ))}
        </div>
      </div>

      {/* Notes */}
      <div className="col-md-6">
        <InputTextField
          className="bg-w"
          label="Notes"
          multiline
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
      </div>

      {/* Actions */}
      <div className="row mt-3">
        <div className="col-6">
          <a
            href="#"
            className="c-r text-decoration-none"
            onClick={(e) => {
              e.preventDefault();
              resetForm();
            }}
          >
            Cancel
          </a>
        </div>

         <div className="col-6 d-flex justify-content-end gap-2">
          <button
            className="btn px-4 bor-dg c-dg fw-md"
            onClick={handleSave}
          >
            Save
          </button>

          <button
            className="btn btn-primary bg-dg fw-md"
            onClick={handleSaveNext}
          >
            Save & Add Next
          </button>
        </div>
      </div>

      {/* Add Medicine Modal */}
      {openModal && (
        <div className="modal fade show d-block" style={{ background: "rgba(0,0,0,.5)" }}>
          <div className="modal-dialog">
            <div className="modal-content p-3">
              <h5 className="fw-b c-dg text-center mb-3">Add New Medicine</h5>

              <InputTextField label="Medicine Name" value={medicine} onChange={(e) => setMedicine(e.target.value)} />
              <InputTextField label="Dosage" className="mt-2" />

              <FormActionButtons
                onCancel={() => setOpenModal(false)}
                onSubmit={() => setOpenModal(false)}
                cancelLabel="Cancel"
                submitLabel="Add Medicine"
              />
            </div>
          </div>
        </div>
      )}

      {/* Status Modal */}
      <StatusModal
        open={openStatus}
        title="Medicine added successfully"
        onClose={() => setOpenStatus(false)}
        buttonText="Continue"
      />
    </div>
  );
};

export default ConsultationMedicines;
