from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.jwt import verify_access_token

# No tokenUrl needed here
security = HTTPBearer()

async def get_current_doctor(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials  # Extract token string
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return payload["doctor_id"]
