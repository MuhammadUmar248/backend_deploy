from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
import re


class CreateDoctor(BaseModel):
    username: str =  Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if len(v) > 128:
            raise ValueError('Password must be less than 128 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if ' ' in v:
            raise ValueError('Password cannot contain spaces')
        return v


class DoctorLogin(BaseModel):
    email: str
    password: str

class DoctorResponse(CreateDoctor):
    id: str
    created_at: int
    updated_at: int

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None