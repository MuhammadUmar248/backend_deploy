from fastapi import APIRouter, HTTPException,status, Depends
from mongodb.connection import prescription_collection
from model.prescription import  CreatePrescription, PrescriptionResponse, UpdatePrescription
from mongodb.connection import patient_collection
from utils.dependency import get_current_doctor
from bson import ObjectId


from datetime import datetime

router = APIRouter()

@router.post("/create", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_prescription(prescription: CreatePrescription, doctor_id: str = Depends(get_current_doctor)):

    try:

        patient = await patient_collection.find_one({
            "_id": ObjectId(prescription.patient_id),
            "doctor_id": doctor_id
        })
        if not patient:
            raise HTTPException(status_code=403, detail="Unauthorized: Patient does not belong to you")

        current_time = int(datetime.now().timestamp())

        medicines_list = [med.model_dump() for med in prescription.medicines]
        prescription_dict = {
            "doctor_id": doctor_id,
            "patient_id": prescription.patient_id,
            "symptoms":prescription.symptoms,
            "medicines": medicines_list,
            "notes": prescription.notes,
            "follow_up_days": prescription.follow_up_days,
            "created_at": current_time,
            "updated_at": current_time
        }

        # Insert into database
        result = await prescription_collection.insert_one(prescription_dict)

        return {
            "message": "Prescription created successfully",
            "Prescription": str(result.inserted_id),
            "status": "success"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.get("/all", response_model=list[PrescriptionResponse])
async def get_all_prescriptions(doctor_id: str = Depends(get_current_doctor)):
    prescriptions = await prescription_collection.find({"doctor_id": doctor_id}).to_list(100)
    return [PrescriptionResponse(**p) for p in prescriptions]

@router.get("/{prescription_id}", response_model=PrescriptionResponse)
async def get_prescription(prescription_id: str, doctor_id: str = Depends(get_current_doctor)):
    if not ObjectId.is_valid(prescription_id):
        raise HTTPException(status_code=400, detail="Invalid prescription ID")

    prescription = await prescription_collection.find_one({
        "_id": ObjectId(prescription_id),
        "doctor_id": doctor_id
    })
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return PrescriptionResponse(**prescription)

@router.put("/{prescription_id}", response_model=dict)
async def update_prescription(prescription_id: str, update: UpdatePrescription, doctor_id: str = Depends(get_current_doctor)):
    if not ObjectId.is_valid(prescription_id):
        raise HTTPException(status_code=400, detail="Invalid prescription ID")

    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    if "doctor_id" in update_data:
        del update_data["doctor_id"]

    update_data["updated_at"] = int(datetime.now().timestamp())

    result = await prescription_collection.update_one(
        {"_id": ObjectId(prescription_id), "doctor_id": doctor_id},
        {"$set": update_data}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Prescription not found or no changes made")
    return {"message": "Prescription updated successfully"}

@router.delete("/{prescription_id}", response_model=dict)
async def delete_prescription(prescription_id: str, doctor_id: str = Depends(get_current_doctor)):
    if not ObjectId.is_valid(prescription_id):
        raise HTTPException(status_code=400, detail="Invalid prescription ID")

    result = await prescription_collection.delete_one({
        "_id": ObjectId(prescription_id),
        "doctor_id": doctor_id
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return {"message": "Prescription deleted successfully"}
