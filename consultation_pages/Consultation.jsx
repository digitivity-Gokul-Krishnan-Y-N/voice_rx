import React, { useState, useEffect } from "react";
import "bootstrap/dist/css/bootstrap.min.css";

import ConsultationDetails from "./ConsultationDetails/ConsultationDetails";
import ConsultationMedicines from "./ConsultationMedicines/AddConsultationMedicines";
import ConsultationTests from "./ConsultationTests/LabTest/AddLabTest";
import ConsultationFollowUp from "./ConsultationFollowUp/ConsultationFollowUp";
import UploadPrescription from "./ConsultationFollowUp/UploadPrescription";
import ConsultationFollowUp_2 from "./ConsultationFollowUp/ConsultationFollowUp_2";

const Consultation = () => {
  const [activeTab, setActiveTab] = useState("details");
  const [isUploadMode, setIsUploadMode] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [extractedData, setExtractedData] = useState(null);

  // Load extracted data on mount
  useEffect(() => {
    loadExtractedData();
  }, []);

  const loadExtractedData = async () => {
    try {
      const response = await fetch("/data/live_consultation_result.json");
      if (response.ok) {
        const data = await response.json();
        setExtractedData(data);
      }
    } catch (error) {
      console.error("Error loading extracted data:", error);
    }
  };

  const handleStartRecording = async () => {
    try {
      setIsRecording(true);
      setLoading(true);
      const response = await fetch("/api/start-consultation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      if (!response.ok) throw new Error("Failed to start recording");
      setLoading(false);
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
      const response = await fetch("/api/stop-consultation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      if (response.ok) {
        const result = await response.json();
        setExtractedData(result);
      }
      setLoading(false);
    } catch (error) {
      console.error("Stop recording error:", error);
      setLoading(false);
    }
  };

  const renderTab = () => {
    if (isUploadMode) {
      if (activeTab === "uploadpres") return <UploadPrescription />;
      if (activeTab === "followup2") return <ConsultationFollowUp_2 />;
      return null;
    }

    switch (activeTab) {
      case "details":
        return <ConsultationDetails extractedData={extractedData} />;
      case "medicines":
        return <ConsultationMedicines extractedData={extractedData} />;
      case "tests":
        return <ConsultationTests extractedData={extractedData} />;
      case "followup":
        return <ConsultationFollowUp extractedData={extractedData} />;
      default:
        return null;
    }
  };

  const handleUploadClick = () => {
    setIsUploadMode(true);
    setActiveTab("uploadpres");
  };

  const handleManualEntry = () => {
    setIsUploadMode(false);
    setActiveTab("details");
  };

  const tabClass = (tab) =>
    `nav-link ${
      activeTab === tab
        ? "active fw-bold bg-bl4 c-dg active-tab-border"
        : "bg-gy1 c-bkl"
    }`;

  return (
    <div className="container">
      {/* Recording Controls - Top Section */}
      {!isUploadMode && (
        <div className="card shadow-sm mb-3 border-0" style={{ backgroundColor: "#f8f9fa" }}>
          <div className="card-body d-flex justify-content-between align-items-center">
            <div>
              <h6 className="mb-0 c-dg fw-bold">
                {isRecording ? "🎤 Recording in progress..." : "🎤 Voice Consultation"}
              </h6>
              {isRecording && (
                <small className="text-muted">Speak clearly for better extraction</small>
              )}
            </div>
            <div className="d-flex gap-2">
              {!isRecording ? (
                <button
                  className="btn c-dg bor-dg"
                  onClick={handleStartRecording}
                  disabled={loading}
                >
                  🔴 Start Recording
                </button>
              ) : (
                <button
                  className="btn btn-danger"
                  onClick={handleStopRecording}
                  disabled={loading}
                >
                  ⏹️ Stop Recording
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {loading && (
        <div className="alert alert-warning mb-3" style={{ backgroundColor: "#fff3cd", color: "#856404" }}>
          ⏳ Processing audio... Please wait.
        </div>
      )}

      {/* Patient Info - Show extracted data */}
      <div className="d-inline-flex gap-4 mb-3 border p-2 px-3 rounded-3 align-items-center shadow-sm" style={{ backgroundColor: "#ffffff" }}>
        <span>
          <strong className="c-dg">
            {extractedData?.patient_name || "Patient A"}
          </strong>
          {extractedData?.age ? `, ${extractedData.age}` : ", 35"} | {extractedData?.gender || "Male"}
        </span>
        {!isUploadMode && (
          <>
            {extractedData?.extraction_method && (
              <span>Method: <strong>{extractedData.extraction_method.toUpperCase()}</strong></span>
            )}
            {extractedData?.confidence && (
              <span>Confidence: <strong>{(extractedData.confidence * 100).toFixed(0)}%</strong></span>
            )}
          </>
        )}
        {isUploadMode && (
          <>
            <span>Token: <strong>17</strong></span>
            <span>Type: <strong>Upload</strong></span>
          </>
        )}
      </div>

      {/* Tabs */}
      <ul className="nav nav-pills mb-1 gap-2">
        {/* NORMAL MODE TABS */}
        {!isUploadMode && (
          <>
            <li className="nav-item">
              <button className={tabClass("details")} onClick={() => setActiveTab("details")}>
                Details
              </button>
            </li>

            <li className="nav-item">
              <button className={tabClass("medicines")} onClick={() => setActiveTab("medicines")}>
                Medicines
              </button>
            </li>

            <li className="nav-item">
              <button className={tabClass("tests")} onClick={() => setActiveTab("tests")}>
                Tests
              </button>
            </li>

            <li className="nav-item">
              <button className={tabClass("followup")} onClick={() => setActiveTab("followup")}>
                Follow-Up
              </button>
            </li>

            <li className="ms-auto">
              <button className="btn bor-dg c-dg" onClick={handleUploadClick}>
                Upload Prescription
              </button>
            </li>
          </>
        )}

        {/* UPLOAD MODE TABS */}
        {isUploadMode && (
          <>
            <li className="nav-item">
              <button
                className={tabClass("uploadpres")}
                onClick={() => setActiveTab("uploadpres")}
              >
                Upload
              </button>
            </li>

            <li className="nav-item">
              <button
                className={tabClass("followup2")}
                onClick={() => setActiveTab("followup2")}
              >
                Follow-Up
              </button>
            </li>

            <li className="ms-auto">
              <button className="btn bor-dg c-dg" onClick={handleManualEntry}>
                Enter Manually
              </button>
            </li>
          </>
        )}
      </ul>

      {/* Content */}
      <div className="card shadow-sm bg-bl4">
        <div className="card-body">
          {renderTab()}
        </div>
      </div>
    </div>
  );
};

export default Consultation;
