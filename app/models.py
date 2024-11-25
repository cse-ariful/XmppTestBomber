from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base

class UserAccount(Base):
    __tablename__ = "user_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    mobile_number = Column(String, unique=True, index=True)
    last_signed_in = Column(DateTime, default=func.now())

class OtpSession(Base):
    __tablename__ = "otp_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String, index=True)
    token = Column(String, unique=True, index=True)
    otp = Column(String)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)