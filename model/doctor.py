from pydantic import BaseModel, EmailStr, Field, validator
from typing  import Optional
import re


class CreateDoctor(BaseModel):
    username: str =  Field(min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(min_length=8)


    @validator('username')
    def validate_username_length(cls, value):
        if len(value) < 3:
            raise ValueError("Name must contain at least 3 characters. Please enter a valid name.")
        if len(value) > 20:
            raise ValueError("Name must not exceed 50 characters.")
        return value


    @validator('email')
    def validate_email_domain(cls, value):
        allowed_domains = ['gmail.com', 'email.com']
        domain = value.split('@')[-1]
        if domain not in allowed_domains:
            raise ValueError("Email must end with 'gmail.com' or 'email.com'")
        return value


    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if len(v) > 128:
            raise ValueError('Password must be less than 128 characters')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one alphabet character')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if ' ' in v:
            raise ValueError('Password cannot contain spaces')
        return v


class DoctorLogin(BaseModel):
    email: str
    password: str

class DoctorResponse(CreateDoctor):
    username: str
    email: EmailStr
    created_at: int
    updated_at: int

class DoctorUpdate(CreateDoctor):
    username: Optional[str]
    email: Optional[EmailStr]

class Token(BaseModel):
    access_token: str
    token_type: str


# class TokenData(BaseModel):
#     user_id: Optional[str] = None