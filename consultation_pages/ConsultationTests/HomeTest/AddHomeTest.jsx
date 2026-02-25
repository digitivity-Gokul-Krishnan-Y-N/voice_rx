import React, { useState } from "react";
import ConsultationMedList from "../../ConsultationMedicines/ConsultationMedList";
import AddMoreDropdownField from "../../../../Components/Interfaces/AddMoreDropdown";
import DropdownField from "../../../../Components/Interfaces/DropdownField";
import InputTextField from "../../../../Components/Interfaces/InputTextField";
import FormActionButtons from "../../../../Components/Interfaces/FormActionButtons";
import StatusModal from "../../../../Components/StatusModal/SuccessStatus";
import AddLabTest from "../LabTest/AddLabTest";

const AddHomeTest = () => {
  const [durationUnit, setDurationUnit] = useState("days");
  const [severity, setSeverity] = useState("");
  const [instructions, setInstructions] = useState([]);
  const [open, setOpen] = useState(false);
  const [frequency, setFrequency] = useState("");
  const [weeklyOption, setWeeklyOption] = useState("");
  const [list, setList] = useState(false);
  const [selectedTests, setSelectedTests] = useState([]);
  const [medicine, setMedicine] = useState("");
  const [openModal, setOpenModal] = useState(false);
  const [openHomeTest, setOpenHomeTest] = useState(false);
  const [TestType, setTestType] = useState("Home");
  const [notes, setNotes] = useState("");

  const units = ["Days", "Weeks", "Until Next Consultation"];

  const handleInstructionChange = (value) => {
    setInstructions((prev) =>
      prev.includes(value)
        ? prev.filter((item) => item !== value)
        : [...prev, value],
    );
  };

  /* ✅ LOG DATA ONLY */
  const logFormData = (action) => {
    const payload = {
      action,
      testType: TestType,
      testName: medicine,
      instructions,
      timings: severity,
      frequency,
      weeklyOption,
      durationUnit,
    };

    console.log("Home Test Data 👉", payload);
  };

  const handleSubmit = () => {
    logFormData("SAVE");
    setList(true);
  };

  if (list && list > 0) {
    return <ConsultationMedList onCancel={() => setList(false)} />;
  }

  if (openHomeTest) {
    return <AddLabTest />;
  }

  return (
    <div className="row g-3">
      <div className="col-12 d-flex justify-content-end align-items-center">
        <a href="#" className="c-dg">
          Skip
        </a>
      </div>

      {/* Test Type */}
      <div className="col-md-6">
        <DropdownField
          label="Test Type"
          onChange={(e) => {
            setOpenHomeTest(e.target.value === "Lab");
            setTestType(e.target.value);
          }}
          options={[
            { value: "Home", label: "Home Test" },
            { value: "Lab", label: "Lab Test" },
          ]}
          value={TestType}
          placeholder="Select test type"
          required
        />
      </div>

      {/* Select Test */}
      <div className="col-md-6">
        <AddMoreDropdownField
          label="Select Test"
          name="test"
          value={medicine}
          options={[
            { value: "test1", label: "Test 1" },
            { value: "test2", label: "Test 2" },
          ]}
          onChange={(e) => setMedicine(e.target.value)}
          onAddMore={() => setOpenModal(true)}
          onSearch={(q) => console.log("search:", q)}
          onScrollEnd={() => console.log("load more")}
          placeholder="Search test"
          className="h-50"
          required
        />
      </div>

      {/* Instructions */}
      <div className="col-md-6">
        <label className="form-label fs-lg fw-b">Instructions</label>
        <div className="border rounded-3 bg-white p-3 mt-1">
          <div className="d-flex gap-4 flex-wrap">
            {["Morning", "Afternoon", "Evening"].map((level) => (
              <div className="form-check" key={level}>
                <input
                  type="checkbox"
                  className="form-check-input"
                  checked={instructions.includes(level)}
                  onChange={() => handleInstructionChange(level)}
                />
                <label className="form-check-label ms-1">{level}</label>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Timings */}
      <div className="col-md-6">
        <label className="form-label fs-lg fw-b">Timings</label>
        <div className="d-flex gap-4 mt-1">
          {["Before Food", "After Food"].map((level) => (
            <div className="form-check" key={level}>
              <input
                type="radio"
                className="form-check-input"
                checked={severity === level}
                onChange={() => setSeverity(level)}
              />
              <label className="form-check-label">{level}</label>
            </div>
          ))}
        </div>
      </div>

      {/* Frequency */}
      <div className="col-md-6">
        <DropdownField
          label="Frequency"
          placeholder="Select frequency"
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
        <label className="form-label fs-lg fw-b">
          Duration <span className="text-danger">*</span>
        </label>

        <div className="d-flex gap-3 align-items-center flex-wrap">
          <input
            className="form-control"
            placeholder="00"
            style={{ width: 60 }}
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
      <div className="row mt-3 align-items-center">
        <div className="col-6">
          <a href="#" className="c-r text-decoration-none">
            Cancel
          </a>
        </div>

        <div className="col-6 d-flex justify-content-end gap-2">
          <button
            type="button"
            className="btn btn-outline-secondary bor-dg c-dg fw-md px-4"
            onClick={handleSubmit}
          >
            Save
          </button>

          <button
            type="button"
            className="btn btn-primary bg-dg fw-md"
            onClick={() => logFormData("SAVE_ADD_NEXT")}
          >
            Save & Add Next
          </button>
        </div>
      </div>

      {/* Modal */}
      {openModal && (
        <div
          className="modal fade show d-block"
          style={{ background: "rgba(0,0,0,0.5)" }}
        >
          <div className="modal-dialog">
            <div className="modal-content p-3">
              <h5 className="fw-b c-dg text-center">Add New Medicine</h5>

              <InputTextField
                label="Medicine Name"
                value={medicine}
                onChange={(e) => setMedicine(e.target.value)}
              />

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

      <StatusModal
        open={open}
        title="You have successfully started the consultation."
        onClose={() => setOpen(false)}
        buttonText="Go to Consultation"
      />
    </div>
  );
};

export default AddHomeTest;
