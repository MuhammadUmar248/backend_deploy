import certifi
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = "mongodb+srv://UmarShafeeq:U08KAH1B4CWPCrdk@cluster0.igzq9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME = "doctor_Management"
# MongoDB connection
client = AsyncIOMotorClient(MONGODB_URL, tls=True, tlsCAFile=certifi.where())
database = client[DATABASE_NAME]
doctor_collection = database["doctor"]
