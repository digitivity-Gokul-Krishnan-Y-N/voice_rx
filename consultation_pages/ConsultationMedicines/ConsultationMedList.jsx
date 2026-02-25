import React, { useState } from 'react'
import MedicineCard from './MedicineCard'
import EditConsultationMedicines from './EditConsultationMedicines'
import DeleteSlotModal from '../../SlotSetup/DeleteSlotModal/DeleteSlotModal';

const ConsultationMedList = ({ onCancel }) => {
    const [Edit, setEdit] = useState(false)
    const [Delete, setDelete] = useState(false)
    const medicine = [
        {
            id: 1,
            name: "Paracetamol",
            dosage: "500 mg",
            instructions: "Morning, Evening",
            timings: "After Food",
            frequency: "Twice a day",
            duration: "7 Days",
            notes: "Take with water"
        },
        {
            id: 2,
            name: "Amoxicillin",
            dosage: "250 mg",
            instructions: "Afternoon",
            timings: "Before Food",
            frequency: "Once a day",
            duration: "5 Days",
            notes: "Complete the course"
        },
        {
            id: 1,
            name: "Paracetamol",
            dosage: "500 mg",
            instructions: "Morning, Evening",
            timings: "After Food",
            frequency: "Twice a day",
            duration: "7 Days",
            notes: "Take with water"
        },
        {
            id: 2,
            name: "Amoxicillin",
            dosage: "250 mg",
            instructions: "Afternoon",
            timings: "Before Food",
            frequency: "Once a day",
            duration: "5 Days",
            notes: "Complete the course"
        }, {
            id: 1,
            name: "Paracetamol",
            dosage: "500 mg",
            instructions: "Morning, Evening",
            timings: "After Food",
            frequency: "Twice a day",
            duration: "7 Days",
            notes: "Take with water"
        },
        {
            id: 2,
            name: "Amoxicillin",
            dosage: "250 mg",
            instructions: "Afternoon",
            timings: "Before Food",
            frequency: "Once a day",
            duration: "5 Days",
            notes: "Complete the course"
        }


    ]

    if (Edit) {
        return <EditConsultationMedicines onCancel={() => setEdit(false)} />;
    }
    return (
        <div className='row '>
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
            {medicine.map((med) => (
                <div className='col-6 mb-4'>
                    <MedicineCard
                        key={med.id}
                        medicine={med}
                        onEdit={() => { console.log("Edit clicked for medicine ID:", med.id); setEdit(true); }}
                        onDelete={() => { console.log("Delete clicked for medicine ID:", med.id); setDelete(true); }}
                    />

                </div>
            ))}
            {Delete && (
                <DeleteSlotModal
                    title="Delete Medicine"
                    message="Are you sure you want to delete this medicine from the consultation?"
                    onCancel={() => setDelete(false)}
                    onConfirm={() => {
                        setDelete(true);
                        // Add deletion logic here
                    }}
                />
            )}
        </div>
    )
}

export default ConsultationMedList