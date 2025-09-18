from fastapi import APIRouter, HTTPException,status
from mongodb.connection import client, doctor_collection
from model.doctor import CreateDoctor, DoctorLogin
from utils.dependency import hash_password, verify_password
from datetime import datetime


router = APIRouter()


@router.on_event("startup")
async def startup_db_client():
    """Create database indexes on startup"""
    # Create unique index on email
    await doctor_collection.create_index("email", unique=True)
    print("Database connected and indexes created!")


@router.on_event("shutdown")
async def shutdown_db_client():
    """Close database connection"""
    client.close()


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_doctor(doctor:CreateDoctor):
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

        # Ensure we return a proper dictionary response
        response_data = {
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
