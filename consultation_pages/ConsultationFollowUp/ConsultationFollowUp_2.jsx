import React, { useState } from "react";
import "react-datepicker/dist/react-datepicker.css";
import InputTextField from "../../../Components/Interfaces/InputTextField";
import StatusModal from "../../../Components/StatusModal/SuccessStatus";

const ConsultationFollowUp_2 = () => {
  const [open, setOpen] = useState(false);

  const [date, setDate] = useState("");
  const [purpose, setPurpose] = useState("");
  const [notes, setNotes] = useState("");

  // 🔹 Reset form
  const resetForm = () => {
    setDate("");
    setPurpose("");
    setNotes("");
  };

  // 🔹 Submit handler
  const handleSubmit = () => {
    console.log("Follow-up Details:", {
      date,
      purpose,
      notes,
    });

    setOpen(true);
    resetForm(); // ✅ clear data after save
  };

  return (
    <div className="row g-3">

      {/* Date */}
      <div className="col-12">
        <div className="col-6">
          <InputTextField
            className="bg-w"
            type="date"
            label="Date"
            placeholder="Enter here"
            value={date}
            onChange={(e) => setDate(e.target.value)}
          />
        </div>
      </div>

      {/* Purpose */}
      <div className="col-md-6">
        <InputTextField
          className="bg-w"
          label="Purpose"
          placeholder="Enter here"
          multiline
          value={purpose}
          onChange={(e) => setPurpose(e.target.value)}
        />
      </div>

      {/* Notes */}
      <div className="col-md-6">
        <InputTextField
          className="bg-w"
          label="Notes"
          placeholder="Enter here"
          multiline
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
      </div>

      {/* Actions */}
      <div className="row mt-3 align-items-center">
        {/* Cancel */}
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

        {/* Submit */}
        <div className="col-6 d-flex justify-content-end gap-2">
          <button
            type="button"
            className="btn btn-primary bg-dg fw-md px-4"
            onClick={handleSubmit}
          >
            Submit
          </button>
        </div>
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

export default ConsultationFollowUp_2;
