from pydantic import BaseModel, EmailStr
from typing import Optional

class SignupRequest(BaseModel):
    full_name: str
    phone_number: str
    email: Optional[EmailStr] = None
    password: str
    confirm_password: str

class LoginRequest(BaseModel):
    phone_number: str
    password: str
