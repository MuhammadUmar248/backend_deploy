import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os


load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = "doctor_Management"
# MongoDB connection
client = AsyncIOMotorClient(MONGODB_URL, tls=True, tlsCAFile=certifi.where())
database = client[DATABASE_NAME]
doctor_collection = database["doctor"]
patient_collection = database["patient"]
prescription_collection = database["prescription"]



