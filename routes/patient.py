from fastapi import APIRouter, HTTPException,status, Depends
from bson import ObjectId
from mongodb.connection import client, patient_collection
from model.patient import PatientResponse, CreatePatient, UpdatePatient
from utils.dependency import get_current_doctor
from datetime import datetime

router = APIRouter()

@router.post("/create", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_patient(patient: CreatePatient, doctor_id: str = Depends(get_current_doctor)):

    try:
        # Check if user already exists
        existing_patient = await patient_collection.find_one({
            "$or": [
                {"email": patient.email.lower()},
                {"username": patient.username.lower()}
            ]
        })
        print(f"Existing doctor found: {existing_patient}")
        if existing_patient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or username already exists"
            )

            # Create user document
        current_time = int(datetime.now().timestamp())
        patient_dict = {
            "doctor_id": doctor_id,
            "username": patient.username.lower(),
            "email": patient.email.lower(),
            "PhoneNumber": patient.PhoneNumber,
            "age": patient.age,
            "gender": patient.gender,
            "weight": patient.weight,
            "created_at": current_time,
            "updated_at": current_time
        }

        # Insert into database
        result = await patient_collection.insert_one(patient_dict)

        return {
            "message": "Patient registered successfully",
            "Patient_id": str(result.inserted_id),
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

# Get all patients for logged-in doctor
@router.get("/all", response_model=list[PatientResponse])
async def get_all_patients(doctor_id: str = Depends(get_current_doctor)):
    patients = await patient_collection.find({"doctor_id": doctor_id}).to_list(100)
    return [PatientResponse(**p) for p in patients]

# Get patient by ID
@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: str, doctor_id: str = Depends(get_current_doctor)):
    if not ObjectId.is_valid(patient_id):
        raise HTTPException(status_code=400, detail="Invalid patient ID")

    patient = await patient_collection.find_one({
        "_id": ObjectId(patient_id),
        "doctor_id": doctor_id
    })
    print("Looking for patient:", patient_id)
    print("Doctor making request:", doctor_id)

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return PatientResponse(**patient)

# Update patient
@router.put("/{patient_id}", response_model=dict)
async def update_patient(patient_id: str, update: UpdatePatient, doctor_id: str = Depends(get_current_doctor)):
    if not ObjectId.is_valid(patient_id):
        raise HTTPException(status_code=400, detail="Invalid patient ID")

    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    # Prevent doctor_id from being overwritten
    if "doctor_id" in update_data:
        del update_data["doctor_id"]

    update_data["updated_at"] = int(datetime.now().timestamp())

    result = await patient_collection.update_one(
        {"_id": ObjectId(patient_id), "doctor_id": doctor_id},
        {"$set": update_data}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found or no changes made")
    return {"message": "Patient updated successfully"}

# Delete patient
@router.delete("/{patient_id}", response_model=dict)
async def delete_patient(patient_id: str, doctor_id: str = Depends(get_current_doctor)):
    if not ObjectId.is_valid(patient_id):
        raise HTTPException(status_code=400, detail="Invalid patient ID")

    result = await patient_collection.delete_one({
        "_id": ObjectId(patient_id),
        "doctor_id": doctor_id
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "Patient deleted successfully"}

