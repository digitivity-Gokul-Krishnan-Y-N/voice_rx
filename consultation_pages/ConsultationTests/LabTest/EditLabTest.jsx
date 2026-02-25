import React, { useState } from "react";
import AddMoreDropdownField from "../../../../Components/Interfaces/AddMoreDropdown";
import DropdownField from "../../../../Components/Interfaces/DropdownField";
import InputTextField from "../../../../Components/Interfaces/InputTextField";
import FormActionButtons from "../../../../Components/Interfaces/FormActionButtons";
import StatusModal from "../../../../Components/StatusModal/SuccessStatus";
import AddHomeTest from "../HomeTest/AddHomeTest";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import TestsList from "../TestsList";

const EditLabTest = () => {
  const [durationUnit, setDurationUnit] = useState("Days");
  const [severity, setSeverity] = useState("");
  const [instructions, setInstructions] = useState([]);
  const [weeklyOption, setWeeklyOption] = useState("");
  const [medicine, setMedicine] = useState("");
  const [timings, setTimings] = useState("");
  const [testType, setTestType] = useState("Lab");
  const [selectedDate, setSelectedDate] = useState(null);
  const [showCalendar, setShowCalendar] = useState(false);

  const [openModal, setOpenModal] = useState(false);
  const [openHomeTest, setOpenHomeTest] = useState(false);
  const [showList, setShowList] = useState(false);
  const [openStatus, setOpenStatus] = useState(false);
    const [notes, setNotes] = useState("")
  

  /* ---------------- RESET FORM ---------------- */
  const resetForm = () => {
    setDurationUnit("Days");
    setSeverity("");
    setInstructions([]);
    setWeeklyOption("");
    setMedicine("");
    setTimings("");
    setSelectedDate(null);
    setShowCalendar(false);
  };

  /* ---------------- SAVE ---------------- */
  const handleSave = () => {
    const payload = {
      testType,
      medicine,
      timings,
      selectedDate,
      durationUnit,
    };

    console.log("Saved Lab Test:", payload);

    resetForm();        // ✅ clear form
    setShowList(true);  // ✅ go to list
  };

  /* ---------------- SAVE & ADD NEXT ---------------- */
  const handleSaveAndNext = () => {
    const payload = {
      testType,
      medicine,
      timings,
      selectedDate,
      durationUnit,
    };

    console.log("Saved & Add Next:", payload);

    resetForm();        // ✅ clear only
    setOpenStatus(true);
  };

  if (showList) {
    return <TestsList onCancel={() => setShowList(false)} />;
  }

  if (openHomeTest) {
    return <AddHomeTest />;
  }

  return (
    <div className="row g-3">

      {/* Test Type */}
      <div className="col-md-6">
        <DropdownField
          label="Test Type"
          value={testType}
          onChange={(e) => {
            setTestType(e.target.value);
            setOpenHomeTest(e.target.value === "Home");
          }}
          options={[
            { value: "Home", label: "Home Test" },
            { value: "Lab", label: "Lab Test" },
          ]}
          required
        />
      </div>

      {/* Select Test */}
      <div className="col-md-6">
        <AddMoreDropdownField
          label="Select Test"
          value={medicine}
          options={[
            { value: "test1", label: "Test 1" },
            { value: "test2", label: "Test 2" },
          ]}
          onChange={(e) => setMedicine(e.target.value)}
          onAddMore={() => setOpenModal(true)}
          placeholder="Search test"
          required
        />
      </div>

      {/* Timing */}
      <div className="col-md-6">
        <DropdownField
          label="Timing"
          value={timings}
          displayValue={
            selectedDate ? selectedDate.toLocaleDateString("en-GB") : null
          }
          onChange={(e) => {
            const val = e.target.value;
            setTimings(val);

            if (val === "specific date") setShowCalendar(true);
            if (val === "immediate") {
              setSelectedDate(null);
              setShowCalendar(false);
            }
          }}
          options={[
            { value: "immediate", label: "Immediate" },
            { value: "specific date", label: "Specific Date" },
          ]}
          required
        />

        {showCalendar && (
          <div className="mt-2">
            <DatePicker
              selected={selectedDate}
              onChange={(date) => {
                setSelectedDate(date);
                setShowCalendar(false);
              }}
              inline
              minDate={new Date()}
            />
          </div>
        )}
      </div>

      {/* Notes */}
      <div className="col-md-6">
         <InputTextField label="Notes" placeholder="Enter here" className="bg-w"  value={notes}
          onChange={(e) => setNotes(e.target.value)} multiline />
      </div>

      {/* Actions */}
      <div className="col-12 d-flex justify-content-between mt-3">
        <a className="c-r" onClick={resetForm}>Cancel</a>

       
         <div className="col-6 d-flex justify-content-end gap-2">
          <button
            className="btn px-4 bor-dg c-dg fw-md"
            onClick={handleSave}
          >
            Save
          </button>

          <button
            className="btn btn-primary bg-dg fw-md"
            onClick={handleSaveAndNext}
          >
            Save & Add Next
          </button>
        </div>
      </div>

      {/* Add Medicine Modal */}
      {openModal && (
        <div className="modal fade show d-block bg-dark bg-opacity-50">
          <div className="modal-dialog">
            <div className="modal-content p-3">
              <InputTextField
                label="Medicine Name"
                value={medicine}
                onChange={(e) => setMedicine(e.target.value)}
              />
              <FormActionButtons
                onCancel={() => setOpenModal(false)}
                onSubmit={() => setOpenModal(false)}
              />
            </div>
          </div>
        </div>
      )}

      {/* Status Modal */}
      <StatusModal
        open={openStatus}
        title="Lab test saved successfully"
        onClose={() => setOpenStatus(false)}
        buttonText="Continue"
      />
    </div>
  );
};

export default EditLabTest;
