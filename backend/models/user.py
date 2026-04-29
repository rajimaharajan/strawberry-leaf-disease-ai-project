from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from passlib.context import CryptContext
import re

# pwd_context moved to core/security.py
# Simplified for email/password signup

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: str
    role: str = Field(..., pattern="^(farmer|agronomist|researcher|admin)$")

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    phone_number: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserOut(UserBase):
    id: str
    email: EmailStr

    class Config:
        from_attributes = True

