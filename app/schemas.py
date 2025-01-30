from typing import List
from pydantic import BaseModel, Field
from datetime import datetime

class UserAccountCreate(BaseModel):
    username: str
    password: str
    mobile_number: str

class OtpRequest(BaseModel):
    mobile_number: str = Field(..., pattern=r'^\+?[1-9]\d{9,14}$')

class OtpVerify(BaseModel):
    token: str
    otp: str

class ContactSyncRequest(BaseModel):
    numbers: List[str]