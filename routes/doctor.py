from fastapi import APIRouter, HTTPException,status, Depends
from mongodb.connection import client, doctor_collection
from bson import ObjectId
from model.doctor import CreateDoctor, DoctorLogin, DoctorResponse, DoctorUpdate
from utils.jwt import create_access_token
from utils.hash_password import hash_password, verify_password
from utils.dependency import get_current_doctor
from datetime import datetime

router = APIRouter()


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_doctor(doctor:CreateDoctor):
    print("Login attempt for:", credentials.email)
    print("Doctor found:", bool(doctor))
    print("Password hash:", doctor.get("password"))

    try:
        # Check if user already exists
        existing_doctor = await doctor_collection.find_one({
            "$or": [
                {"email": doctor.email.lower()},
                {"username": doctor.username.lower()}
            ]
        })
        print(f"Existing doctor found: {existing_doctor}")
        if existing_doctor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or username already exists"
            )


        hashed_password = hash_password(doctor.password)

        # Create user document
        current_time = int(datetime.now().timestamp())
        doctor_dict = {
            "username": doctor.username.lower(),
            "email": doctor.email.lower(),
            "password": hashed_password,  # Stored as hash
            "created_at": current_time,
            "updated_at": current_time
        }
        # Insert into database
        result = await doctor_collection.insert_one(doctor_dict)

        return {
            "message": "User registered successfully",
            "user_id": str(result.inserted_id),
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


@router.post("/login", response_model=dict)
async def login_doctor(credentials: DoctorLogin):
    """Authenticate doctor and return access token"""
    try:
        print(f"Login attempt for email: {credentials.email}")

        # Find doctor by email
        doctor = await doctor_collection.find_one({"email": credentials.email.lower()})
        print(f"User found: {doctor is not None}")
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Verify password
        if not verify_password(credentials.password, doctor.get("password")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        token = create_access_token({"doctor_id": str(doctor["_id"])})

        # Ensure we return a proper dictionary response

        response_data = {
            "token": {"access_token": token, "token_type": "bearer"},
            "email": doctor["email"].lower(),
        }
        print(f"Login successful, returning: {response_data}")


        return response_data

    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/all", response_model=list[DoctorResponse])
async def get_all_doctors():
    doctors = await doctor_collection.find().to_list(100)
    return [DoctorResponse(**doc) for doc in doctors]

# Get doctor profile
@router.get("/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(doctor_id: str):
    doctor = await doctor_collection.find_one({"_id": ObjectId(doctor_id)})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return DoctorResponse(**doctor)

# Update doctor profile
@router.put("/{doctor_id}", response_model=dict)
async def update_doctor(doctor_id: str, update: DoctorUpdate, current_id: str = Depends(get_current_doctor)):
    if doctor_id != current_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    update_data["updated_at"] = int(datetime.now().timestamp())

    result = await doctor_collection.update_one(
        {"_id": ObjectId(doctor_id)},
        {"$set": update_data}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="No changes made")
    return {"message": "Doctor updated successfully"}

# Delete doctor
@router.delete("/{doctor_id}", response_model=dict)
async def delete_doctor(doctor_id: str, current_id: str = Depends(get_current_doctor)):
    if doctor_id != current_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    result = await doctor_collection.delete_one({"_id": ObjectId(doctor_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return {"message": "Doctor deleted successfully"}

