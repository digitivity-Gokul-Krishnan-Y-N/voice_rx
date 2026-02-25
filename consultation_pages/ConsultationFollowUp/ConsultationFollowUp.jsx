import React, { useState, useEffect } from "react";
import "react-datepicker/dist/react-datepicker.css";
import StatusModal from "../../../Components/StatusModal/SuccessStatus";
import InputTextField from "../../../Components/Interfaces/InputTextField";
import Prescription from "./PreviewPrescription";
import * as html2pdf from "html2pdf.js";

const ConsultationFollowUp = ({ extractedData = null }) => {
  const [open, setOpen] = useState(false);
  const [openModal, setOpenModal] = useState(false);

  // Get today's date for consultation date
  const [consultationDate] = useState(new Date().toISOString().split('T')[0]);
  const [date, setDate] = useState("");
  const [purpose, setPurpose] = useState("");
  const [notes, setNotes] = useState("");
  const [extractedAdvice, setExtractedAdvice] = useState([]);

  // Auto-fill advice from extracted data
  useEffect(() => {
    if (extractedData?.advice?.length > 0) {
      setExtractedAdvice(extractedData.advice);
      setNotes(extractedData.advice.join("\n"));
    }
  }, [extractedData]);

  // 🔹 Reset form
  const resetForm = () => {
    setDate("");
    setPurpose("");
    setNotes("");
  };

  // 🔹 Save & Add Next
  const handleSaveNext = () => {
    console.log("Follow-up Data:", {
      date,
      purpose,
      notes,
    });

    setOpen(true);
    resetForm();
  };

  // 🔹 Preview Prescription
  const handlePreview = () => {
    setOpenModal(true);
  };

  // 🔹 Export PDF
  const exportPDF = () => {
    const element = document.getElementById("prescription-pdf");

    const options = {
      margin: [10, 10, 10, 10],
      filename: "Prescription.pdf",
      image: { type: "jpeg", quality: 0.98 },
      html2canvas: {
        scale: 2,
        useCORS: true,
      },
      jsPDF: {
        unit: "mm",
        format: "a4",
        orientation: "portrait",
      },
      pagebreak: {
        mode: ["css", "legacy"],
      },
    };

    html2pdf().set(options).from(element).save();
  };

  return (
    <div className="row g-3">
      {/* Auto-filled advice from extracted data */}
      {extractedAdvice.length > 0 && (
        <div className="col-12">
          <div className="alert alert-warning bg-bl4 border-0">
            <h6 className="fw-b c-dg mb-2">✓ Advice from consultation:</h6>
            <ul className="mb-0 ps-3">
              {extractedAdvice.map((adv, idx) => (
                <li key={idx}><small>{adv}</small></li>
              ))}
            </ul>
          </div>
        </div>
      )}

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

        {/* Buttons */}
        <div className="col-6 d-flex justify-content-end gap-2">
          <button
            type="button"
            className="btn btn-outline-secondary bor-dg c-dg fw-md px-5"
            onClick={handlePreview}
          >
            Preview Prescription
          </button>

          <button
            type="button"
            className="btn btn-primary bg-dg fw-md"
            onClick={handleSaveNext}
          >
            Save & Add Next
          </button>
        </div>
      </div>

      {/* Prescription Preview Modal */}
      {openModal && (
        <>
          <div className="modal fade show d-block" role="dialog">
            <div className="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable w-75">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title">Prescription</h5>
                  <button
                    className="btn-close"
                    onClick={() => setOpenModal(false)}
                  ></button>
                </div>

                <div id="prescription-pdf" className="modal-body p-0">
                  <div className="print-page">
                    <Prescription followupDate={date} consultationDate={consultationDate} />
                  </div>
                </div>

                <div className="modal-footer">
                  <button
                    className="btn btn-outline-secondary bor-dg c-dg fw-md px-5"
                    onClick={() => window.print()}
                  >
                    Print Prescription
                  </button>
                  <button
                    className="btn btn-primary bg-dg fw-md"
                    onClick={exportPDF}
                  >
                    Download Prescription
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div className="modal-backdrop fade show"></div>
        </>
      )}

      {/* Status Modal */}
      <StatusModal
        open={open}
        title="Follow-up saved successfully."
        onClose={() => setOpen(false)}
        buttonText="Go to Consultation"
      />
    </div>
  );
};

export default ConsultationFollowUp;
