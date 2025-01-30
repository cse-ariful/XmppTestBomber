from datetime import datetime
import os
import sys
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from .models import Base, UserAccount, OtpSession
from .schemas import ContactSyncRequest, OtpRequest, OtpVerify
from .database import engine, get_db
from .services.otp_service import OTPService
from .bomber import router
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="frontend"), name="frontend")
app.include_router(router=router,prefix="/bomber")
@app.post("/send-verification-code")
def verify_mobile(
    request: OtpRequest, 
    db: Session = Depends(get_db)
):
    # Create OTP session
    session = OTPService.create_otp_session(db, request.mobile_number)
    
    # In production, send OTP via SMS
    # For demo, we'll return the OTP
    return {
        "token": session.token,
        "otp": session.otp  # Remove this in production
    }

@app.post("/verify-otp")
def verify_otp(
    verify: OtpVerify, 
    db: Session = Depends(get_db)
):
    otp_session = OTPService.verify_otp(db, verify.token, verify.otp)
    if otp_session is not None:
        user = db.query(UserAccount).filter(
           UserAccount.mobile_number == otp_session.mobile_number
        ).first()
        if user is None:
            user = UserAccount()
            user = UserAccount(
            username=  f"{otp_session.mobile_number}@localhost",
            password = "admin",
            mobile_number = otp_session.mobile_number,
            last_signed_in = datetime.now()
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return {
            "username": user.username,
            "password": user.password
        }
    raise HTTPException(status_code=400, detail="Invalid OTP")

@app.post("/lookup-users")
def lookup_users(
    number: ContactSyncRequest, 
    db: Session = Depends(get_db)
):
    flatNumbers = [num.lstrip('+') for num in number.numbers]
    # Query users based on mobile numbers
    users = db.query(UserAccount).filter(
        UserAccount.mobile_number.in_(flatNumbers)
    ).all()

    # Create result list with mobile number and username
    result = [
        {
            "mobile_number": user.mobile_number, 
            "username": user.username
        } for user in users
    ]

    return result

@app.get("/users")
def list_users( 
    db: Session = Depends(get_db)
):
    # Query users based on mobile numbers
    users = db.query(UserAccount).all()

    # Create result list with mobile number and username
    result = [
        {
            "mobile_number": user.mobile_number, 
            "username": user.username,
            "password" : user.password
        } for user in users
    ]

    return result