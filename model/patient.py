from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
import re


class CreatePatient(BaseModel):
    username: str =  Field(min_length=3, max_length=30)
    email: EmailStr
    PhoneNumber: str = Field(min_length=11, max_length=11)
    age: int = Field(ge=1, le=999)
    gender: str = Field(min_length=1, max_length=10)
    weight: int = Field(ge=1, le=999)

    @validator('username')
    def validate_username_length(cls, value):
        if len(value) < 3:
            raise ValueError("Name must contain at least 3 characters. Please enter a valid name.")
        if len(value) > 30:
            raise ValueError("Name must not exceed 30 characters.")
        return value

    @validator('email')
    def validate_email_domain(cls, value):
        allowed_domains = ['gmail.com', 'email.com']
        domain = value.split('@')[-1]
        if domain not in allowed_domains:
            raise ValueError("Email must end with 'gmail.com' or 'email.com'")
        return value


    @validator('PhoneNumber')
    def check_phone_number(cls, value):
        # Check if it matches exactly 11 digits
        if not re.match(r'^[0-9]{11}$', value):
            raise ValueError("Enter complete number with exactly 11 digits.")
        # Check if it starts with '03'
        if not value.startswith('03'):
            raise ValueError("Phone number must start with '03XX-XXXXXXX'.")
        return value

    @validator('age')
    def validate_age(cls, value):
        if value < 1:
            raise ValueError("Please enter correct age (minimum is 1)")
        if value > 999:
            raise ValueError("Exceeded age limit (maximum is 999)")
        return value

    @validator('weight')
    def validate_weight(cls, value):
        if value < 1:
            raise ValueError("Please enter correct weight (minimum is 1)")
        if value > 999:
            raise ValueError("Exceeded weight limit (maximum is 999)")
        return value

    @validator('gender')
    def validate_gender(cls, value):
        if len(value.strip()) == 0:
            raise ValueError("Gender cannot be empty")
        if len(value) > 10:
            raise ValueError("Gender must not exceed 10 characters")
        return value

class UpdatePatient(CreatePatient):
    username: Optional[str]
    email: Optional[EmailStr]
    PhoneNumber: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    weight: Optional[float]

class PatientResponse(CreatePatient):
    username: str
    email: EmailStr
    PhoneNumber: str
    age: int
    gender: str
    weight: int
    created_at: int
    updated_at: int
