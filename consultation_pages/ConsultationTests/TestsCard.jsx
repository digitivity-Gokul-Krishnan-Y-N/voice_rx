import React from 'react';

const TestsCard = ({ Tests ,onEdit,onDelete}) => {
  // Default data in case props are missing
  const data = Tests || {
    id: 1,
    name: "Test D",
    dosage: "Dosage C",
    instructions: "Morning, Afternoon",
    timings: "After Food",
    frequency: "Daily",
    duration: "20 Days",
    notes: "Will display here"
  };

  return (
    <div className="card border-0 shadow-sm mx-auto" style={{ minWidth: '400px', borderRadius: '20px' }}>
      <div className="card-body p-4">
        {/* Header */}
   <div className="d-flex justify-content-between align-items-center mb-1">
        <h5
            className="card-title mb-0"
            style={{ color: "#5a809e", fontWeight: "600" }}
        >
            Test {data.id}
        </h5>

      
            <i className={`bi bi-bookmark-fill ${
            data.type === "Home"
                ? "text-success"
                : "text-warning "
            }`}></i>
        </div>



       {Tests.type==="Home" ?
       <div>
         {/* Row 1: Name and Dosage */}
        <div className="row mb-2">
            <div className="col-6">
            <small className="text-secondary d-block">Test Type</small>
            <span className="fw-semibold text-dark">{data.type}</span>
          </div>
          <div className="col-6">
            <small className="text-secondary d-block">Test Name</small>
            <span className="fw-semibold text-dark">{data.name}</span>
          </div>
          
        </div>

        <hr className="opacity-10" />

        {/* Row 2: Instructions and Timings */}
        <div className="row mb-2">
          <div className="col-6">
            <small className="text-secondary d-block">Instructions</small>
            <span className="fw-semibold text-dark">{data.instructions}</span>
          </div>
          <div className="col-6">
            <small className="text-secondary d-block">Timings</small>
            <span className="fw-semibold text-dark">{data.timings}</span>
          </div>
        </div>

        <hr className="opacity-10" />

        {/* Row 3: Frequency and Duration */}
        <div className="row mb-2">
          <div className="col-6">
            <small className="text-secondary d-block">Frequency</small>
            <span className="fw-semibold text-dark">{data.frequency}</span>
          </div>
          <div className="col-6">
            <small className="text-secondary d-block">Durations</small>
            <span className="fw-semibold text-dark">{data.duration}</span>
          </div>
        </div>

        <hr className="opacity-10" />

        {/* Notes */}
        <div className="mb-4">
          <small className="text-secondary d-block">Notes</small>
          <span className="fw-semibold text-dark">{data.notes}</span>
        </div>

       </div>:
       <div>
          {/* Row 1: Name and Dosage */}
        <div className="row mb-2">
            <div className="col-6">
            <small className="text-secondary d-block">Test Type</small>
            <span className="fw-semibold text-dark">{data.type}</span>
          </div>
          <div className="col-6">
            <small className="text-secondary d-block">Test Name</small>
            <span className="fw-semibold text-dark">{data.name}</span>
          </div>
          
        </div>
        <hr className="opacity-10" />
         {/* Row 2: Instructions and Timings */}
        <div className="row mb-2">
          <div className="col-6">
            <small className="text-secondary d-block">Timings</small>
            <span className="fw-semibold text-dark">{data.timings}</span>
          </div>
          <div className="mb-4 col-6">
          <small className="text-secondary d-block">Notes</small>
          <span className="fw-semibold text-dark">{data.notes}</span>
        </div>
        </div>

       </div>
       }

        {/* Actions */}
        <div className="d-flex justify-content-end gap-3 mt-3">
          <button 
            className="btn btn-link p-0 text-dark" 
            onClick={onEdit}
            aria-label="Edit"
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
          </button>
          <button 
            className="btn btn-link p-0 text-danger" 
            onClick={onDelete}
            aria-label="Delete"
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
              <line x1="10" y1="11" x2="10" y2="17"></line>
              <line x1="14" y1="11" x2="14" y2="17"></line>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default TestsCard;