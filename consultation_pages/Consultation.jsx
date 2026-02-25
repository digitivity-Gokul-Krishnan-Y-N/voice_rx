import React from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import ConsultationIntegrated from "./ConsultationIntegrated";

const Consultation = () => {
  // ✅ NEW: Single-page consultation with voice recording, auto-fill, and inline editing
  return (
    <div className="container-fluid">      <ConsultationIntegrated />
    </div>
  );
};

export default Consultation;
