from fastapi import FastAPI
from mongodb.connection import doctor_collection
from mongodb.connection import client
from routes.doctor import router as doctor_router
from routes.patient import router as patient_router
from routes.prescription import router as prescription_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    """Create database indexes on startup"""
    # Create unique index on email
    await doctor_collection.create_index("email", unique=True)
    print("Database connected and indexes created!")


@app.on_event("shutdown")
async def shutdown_db_client():
    """Close database connection"""
    client.close()


origins = [
    "http://localhost:3000",  # React dev server
    "https://your-frontend-domain.vercel.app"  # deployed frontend (if applicable)
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(doctor_router, prefix="/doctor")
app.include_router(patient_router, prefix="/patient")
app.include_router(prescription_router, prefix="/prescription")