import React, { useState } from 'react'
import DeleteSlotModal from '../../SlotSetup/DeleteSlotModal/DeleteSlotModal';
import TestsCard from './TestsCard';
import EditLabTest from './LabTest/EditLabTest';
import EditHomeTest from './HomeTest/EditHomeTest';
const tests=[
        {
            id: 1,
            type: "Home",
            name: "Blood Test",
            instructions: "Fasting required",
            timings: "Morning",
            frequency: "Once",
            duration: "1 Day",
            notes: "Handle with care"
        },
        {
            id: 2,
            type: "Lab",
            name: "X-Ray",
            instructions: "No special instructions",
            timings: "Afternoon",
            frequency: "Once",
            duration: "1 Day",
            notes: "Inform technician of any allergies"
        },
        {
            id: 1,
            type: "Home",
            name: "Blood Test",
            instructions: "Fasting required",
            timings: "Morning",
            frequency: "Once",
            duration: "1 Day",
            notes: "Handle with care"
        },
        {
            id: 1,
            type: "Home",
            name: "Blood Test",
            instructions: "Fasting required",
            timings: "Morning",
            frequency: "Once",
            duration: "1 Day",
            notes: "Handle with care"
        },
    ];
const TestsList = ({ onCancel }) => {
  const [edit, setEdit] = useState(false);
  const [deleteModal, setDeleteModal] = useState(false);
  const [selectedTest, setSelectedTest] = useState(null);

  if (edit && selectedTest?.type === "Home") {
    return <EditHomeTest onCancel={() => setEdit(false)} />;
  }

  if (edit && selectedTest?.type === "Lab") {
    return <EditLabTest onCancel={() => setEdit(false)} />;
  }

  return (
    <div className="row">
      <div className="col-12 d-flex justify-content-end mb-3">
        <a
          href="#"
          className="c-dg text-decoration-none fw-semibold"
          onClick={(e) => {
            e.preventDefault();
            onCancel();
          }}
        >
          + Add New Medicine
        </a>
      </div>

      {tests.map((test) => (
        <div className="col-6 mb-4" key={test.id}>
          <TestsCard
            Tests={test}
            onEdit={() => {
              setSelectedTest(test);
              setEdit(true);
            }}
            onDelete={() => {
              setSelectedTest(test);
              setDeleteModal(true);
            }}
          />
        </div>
      ))}

      {deleteModal && (
        <DeleteSlotModal
          title="Delete Test"
          message="Are you sure you want to delete this test from the consultation?"
          onCancel={() => setDeleteModal(false)}
          onConfirm={() => setDeleteModal(true)}
        />
      )}
    </div>
  );
};

export default TestsList