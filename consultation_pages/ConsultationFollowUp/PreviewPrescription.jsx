import logo from "../../../Assets/Images/Images/DigiDoc.svg";
import React from "react";

const Prescription = ({ followupDate = "01/12/2025", consultationDate = "" }) => {
  // Format dates for display
  const formatDate = (dateStr) => {
    if (!dateStr) return "";
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit', year: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  const formattedFollowupDate = formatDate(followupDate);
  const formattedConsultationDate = formatDate(consultationDate);
  const doctor = {
    name: "Dr. Aarvin K. Rao",
    degree: "MBBS",
    specialization: "General Practitioner",
    regNo: "TNMC 204876",
    clinic: "DigiDoc Virtual Clinic - Tamilnadu",
    address: "PixelCare Innovation Park, Block B, 3rd Avenue, Chennai - 600078",
    phone: "+91 98765 43210",
    email: "doc@digidoc.com",
  };

  const patient = {
    name: "Patient A",
    age: 35,
    gender: "Male",
    token: 17,
    type: "In-Person",
    date: "17 Nov 2025",
    time: "10:00 AM",
  };

  const medicines = [
    {
      name: "Medicine D",
      dosage: "Dosage C",
      instruction: "M E",
      timing: "A.F",
      frequency: "Weekly Twice",
      duration: "Until Next Visit",
    },
    {
      name: "Medicine C",
      dosage: "Dosage C",
      instruction: "M A E",
      timing: "A.F",
      frequency: "Weekly Twice",
      duration: "Until Next Visit",
    },
    {
      name: "Medicine D",
      dosage: "Dosage C",
      instruction: "M E",
      timing: "A.F",
      frequency: "Weekly Twice",
      duration: "Until Next Visit",
    },
    {
      name: "Medicine C",
      dosage: "Dosage C",
      instruction: "M A E",
      timing: "A.F",
      frequency: "Weekly Twice",
      duration: "Until Next Visit",
    },
    {
      name: "Medicine D",
      dosage: "Dosage C",
      instruction: "M E",
      timing: "A.F",
      frequency: "Weekly Twice",
      duration: "Until Next Visit",
    },
    {
      name: "Medicine C",
      dosage: "Dosage C",
      instruction: "M A E",
      timing: "A.F",
      frequency: "Weekly Twice",
      duration: "Until Next Visit",
    },
    {
      name: "Medicine D",
      dosage: "Dosage C",
      instruction: "M E",
      timing: "A.F",
      frequency: "Weekly Twice",
      duration: "Until Next Visit",
    },
    {
      name: "Medicine C",
      dosage: "Dosage C",
      instruction: "M A E",
      timing: "A.F",
      frequency: "Weekly Twice",
      duration: "Until Next Visit",
    },
    {
      name: "Medicine D",
      dosage: "Dosage C",
      instruction: "M E",
      timing: "A.F",
      frequency: "Weekly Twice",
      duration: "Until Next Visit",
    },
    {
      name: "Medicine C",
      dosage: "Dosage C",
      instruction: "M A E",
      timing: "A.F",
      frequency: "Weekly Twice",
      duration: "Until Next Visit",
    },
    {
      name: "Medicine D",
      dosage: "Dosage C",
      instruction: "M E",
      timing: "A.F",
      frequency: "Weekly Twice",
      duration: "Until Next Visit",
    },
    {
      name: "Medicine C",
      dosage: "Dosage C",
      instruction: "M A E",
      timing: "A.F",
      frequency: "Weekly Twice",
      duration: "Until Next Visit",
    },
    {
      name: "Medicine D",
      dosage: "Dosage C",
      instruction: "M E",
      timing: "A.F",
      frequency: "Weekly Twice",
      duration: "Until Next Visit",
    },
    {
      name: "Medicine C",
      dosage: "Dosage C",
      instruction: "M A E",
      timing: "A.F",
      frequency: "Weekly Twice",
      duration: "Until Next Visit",
    },
    {
      name: "Medicine D",
      dosage: "Dosage C",
      instruction: "M E",
      timing: "A.F",
      frequency: "Weekly Twice",
      duration: "Until Next Visit",
    },
    {
      name: "Medicine C",
      dosage: "Dosage C",
      instruction: "M A E",
      timing: "A.F",
      frequency: "Weekly Twice",
      duration: "Until Next Visit",
    },
    {
      name: "Medicine D",
      dosage: "Dosage C",
      instruction: "M E",
      timing: "A.F",
      frequency: "Weekly Twice",
      duration: "Until Next Visit",
    },
    {
      name: "Medicine C",
      dosage: "Dosage C",
      instruction: "M A E",
      timing: "A.F",
      frequency: "Weekly Twice",
      duration: "Until Next Visit",
    },
    {
      name: "Medicine D",
      dosage: "Dosage C",
      instruction: "M E",
      timing: "A.F",
      frequency: "Weekly Twice",
      duration: "Until Next Visit",
    },
    {
      name: "Medicine C",
      dosage: "Dosage C",
      instruction: "M A E",
      timing: "A.F",
      frequency: "Weekly Twice",
      duration: "Until Next Visit",
    },
    {
      name: "Medicine D",
      dosage: "Dosage C",
      instruction: "M E",
      timing: "A.F",
      frequency: "Weekly Twice",
      duration: "Until Next Visit",
    },
    {
      name: "Medicine C",
      dosage: "Dosage C",
      instruction: "M A E",
      timing: "A.F",
      frequency: "Weekly Twice",
      duration: "Until Next Visit",
    },
  ];

  const tests = [
    {
      type: "Home",
      name: "Test A, Test B",
      instruction: "M E",
      timing: "A.F",
      frequency: "Daily",
      duration: "2 Months",
    },
    {
      type: "Lab",
      name: "Test C",
      instruction: "-",
      timing: "B.N.C",
      frequency: "-",
      duration: "-",
    },
  ];

  return (
    <div className="container  p-3 bg-w">
      {/* Header */}
      <div className="row border-bottom pb-3 mb-3 ">
        <div className="col-md-3 d-flex align-items-center">
          <img
            src={logo}
            alt="img"
            style={{ width: "145px", height: "42px", objectFit: "contain" }}
          />
        </div>

        <div className="col-md-4">
          <h5 className="mb-0">{doctor.name}</h5>
          <small className="text-muted d-block">{doctor.degree}</small>
          <small className="text-muted d-block">{doctor.specialization}</small>
          <small className="text-muted">Reg.No: {doctor.regNo}</small>
        </div>
        <div className="col-md-5 text-md-end mt-3 mt-md-0">
          <strong>{doctor.clinic}</strong>
          <div className="small">{doctor.address}</div>
          <div className="small">{doctor.phone}</div>
          <div className="small">{doctor.email}</div>
        </div>
      </div>

      {/* Patient Details */}
      <div className="card mb-3">
        <div className="card-body">
          <h6 className="card-titl fw-b">Patient Details</h6>
          <div className="d-flex flex-wrap gap-3 small">
            <span>
              <strong>{patient.name}</strong>{" "}
              {/* <span className=""> ,</span> */}
            </span>
            <span>
              {/* <strong>Age:</strong>{" "} */}
              <span className="text-muted">{patient.age} ,</span>
            </span>
            {/* <span className="mx-1 text-muted">|</span> */}
            <span>
              {/* <strong>Gender:</strong>{" "} */}
              <span className="text-muted">{patient.gender}</span>
            </span>
            <span className="mx-1 text-muted">|</span>
            <span>
              <strong>Token:</strong>{" "}
              <span className="text-muted">{patient.token}</span>
            </span>
            <span className="mx-1 text-muted">|</span>
            <span>
              <strong>Type:</strong>{" "}
              <span className="text-muted">{patient.type}</span>
            </span>
            <span className="mx-1 text-muted">|</span>
            <span>
              <strong>Date:</strong>{" "}
              <span className="text-muted">{patient.date}</span>
            </span>
            <span className="mx-1 text-muted">|</span>
            <span>
              <strong>Time:</strong>{" "}
              <span className="text-muted">{patient.time}</span>
            </span>
          </div>
        </div>
      </div>

      {/* Subjective Data */}
      <div className="card mb-3">
        <div className="card-body">
          <h6 className="card-title fw-b">Primary Subjective Data</h6>
         <div className="container">
  <div className="row gx-2 gy-2">
    {["Complaint", "Medical History", "Diagnosis", "Notes"].map((label, i) => (
      <div className="col-3" key={i}>
        <strong className="d-block mb-1">{label}</strong>
        <textarea
          className="form-control form-control-sm w-100 lh-sm overflow-hidden"
          placeholder={label}
          style={{ height: "55px", maxWidth: "100%" }}
        />
      </div>
    ))}
  </div>
</div>
          <div className="mt-2 small">
            <span className="me-4">Duration: 5 Hours</span>
            <span>Severity: Mild</span>
          </div>
        </div>
      </div>

      {/* Medication */}
      <div className="card mb-3">
        <div className="card-body">
          <h6 className="card-title">Medication Prescribed</h6>
          <div className="table-responsive">
            <table className="table table-sm table-bordered text-center align-middle">
              <thead className="dg-header">
                <tr>
                  <th>S.No</th>
                  <th>Medicine</th>
                  <th>Dosage</th>
                  <th>Instructions</th>
                  <th>Timings</th>
                  <th>Frequency</th>
                  <th>Duration</th>
                </tr>
              </thead>
              <tbody>
                {medicines.map((m, i) => (
                  <tr key={i}>
                    <td>{String(i + 1).padStart(2, "0")}</td>
                    <td>{m.name}</td>
                    <td>{m.dosage}</td>
                    <td>{m.instruction}</td>
                    <td>{m.timing}</td>
                    <td>{m.frequency}</td>
                    <td>{m.duration}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Tests */}
      <div className="card mb-3">
        <div className="card-body">
          <h6 className="card-title">Test Prescribed</h6>
          <div className="table-responsive">
            <table className="table table-sm table-bordered text-center align-middle">
              <thead className="dg-header">
                <tr>
                  <th>S.No</th>
                  <th>Type</th>
                  <th>Test Name</th>
                  <th>Instructions</th>
                  <th>Timings</th>
                  <th>Frequency</th>
                  <th>Duration</th>
                </tr>
              </thead>
              <tbody>
                {tests.map((t, i) => (
                  <tr key={i}>
                    <td>{String(i + 1).padStart(2, "0")}</td>
                    <td>{t.type}</td>
                    <td>{t.name}</td>
                    <td>{t.instruction}</td>
                    <td>{t.timing}</td>
                    <td>{t.frequency}</td>
                    <td>{t.duration}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Follow Up */}
    <div className="card">
  <div className="card-body">

    <h6 className="mb-2">Follow Up</h6>

    <div className="row align-items-end gx-2">

      {/* Left side */}
      <div className="col-9">
        <div className="row align-items-end gx-2">
          <div className="col-3">
            <p className="small mb-1">
              Date: {formattedConsultationDate} to {formattedFollowupDate}
            </p>
          </div>

          <div className="col-4">
            <textarea
              className="form-control form-control-sm w-100 overflow-hidden"
              placeholder="Purpose"
            />
          </div>

          <div className="col-4">
            <textarea
              className="form-control form-control-sm w-100 overflow-hidden"
              placeholder="Notes"
            />
          </div>
        </div>
      </div>

      {/* Right side */}
      <div className="col-3 text-center">
        <div className="border-top pt-1 px-3 small">
          Signature
        </div>
      </div>

    </div>
  </div>
</div>

      <p className="small text-muted mt-3">
        This prescription is digitally generated and valid as per the advised
        dosage and duration.
      </p>
    </div>
  );
};

export default Prescription;
