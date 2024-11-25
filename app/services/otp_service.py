import secrets
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import OtpSession

class OTPService:
    @staticmethod
    def generate_token() -> str:
        return secrets.token_urlsafe(16)

    @staticmethod
    def generate_otp(length: int = 6) -> str:
        return ''.join(secrets.choice(string.digits) for _ in range(length))

    @staticmethod
    def create_otp_session(
        db: Session, 
        mobile_number: str
    ) -> OtpSession:
        # Delete existing sessions for this mobile number
        db.query(OtpSession).filter(
            OtpSession.mobile_number == mobile_number
        ).delete()

        # Create new OTP session
        otp = OTPService.generate_otp()
        token = OTPService.generate_token()
        expires_at = datetime.now() + timedelta(minutes=10)

        otp_session = OtpSession(
            mobile_number=mobile_number,
            token=token,
            otp=otp,
            is_verified=False,
            expires_at=expires_at
        )
        
        db.add(otp_session)
        db.commit()
        db.refresh(otp_session)
        return otp_session

    @staticmethod
    def verify_otp(
        db: Session, 
        token: str, 
        otp: str
    ) -> OtpSession:
        # Find the OTP session
        session = db.query(OtpSession).filter(
            OtpSession.token == token,
            OtpSession.otp == otp,
            OtpSession.is_verified == False,
            OtpSession.expires_at > datetime.now()
        ).first()

        if session:
            # Mark session as verified
            session.is_verified = True
            db.commit()
            return session
        return None