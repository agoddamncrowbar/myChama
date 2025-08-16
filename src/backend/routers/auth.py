from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.auth import SignupRequest, LoginRequest
from database import get_db
from models import User
from auth import hash_password, verify_password, create_access_token
import pyotp
from utils.emai_utils import send_email
from pydantic import BaseModel

router = APIRouter()

@router.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    if data.password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    if db.query(User).filter(User.phone_number == data.phone_number).first():
        raise HTTPException(status_code=400, detail="Phone number already registered")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    # Generate TOTP secret
    secret = pyotp.random_base32()
    otp = pyotp.TOTP(secret).now()
    send_email(
        data.email,
        "Verify Your MyChama Email",
        f"Your verification code is: {otp}"
    )
    new_user = User(
        full_name=data.full_name,
        email=data.email,
        phone_number=data.phone_number,
        password_hash=hash_password(data.password),
        email_verification_secret=secret
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Signup successful. Check your email for a verification code."}

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone_number == data.phone_number).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid phone number or password")
    token = create_access_token({"user_id": user.user_id})
    return {"access_token": token, "token_type": "bearer"}

class VerifyEmailRequest(BaseModel):
    email: str
    code: str

class ResendVerificationRequest(BaseModel):
    email: str

@router.post("/resend-verification")
def resend_verification(data: ResendVerificationRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.email_verified:
        raise HTTPException(status_code=400, detail="Email is already verified")
    
    # Generate new OTP using existing secret
    totp = pyotp.TOTP(user.email_verification_secret)
    otp = totp.now()
    
    send_email(
        user.email,
        "Verify Your MyChama Email - Resent",
        f"Your verification code is: {otp}"
    )
    
    return {"message": "Verification code sent to your email"}

@router.post("/verify-email")
def verify_email(data: VerifyEmailRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    totp = pyotp.TOTP(user.email_verification_secret)
    if totp.verify(data.code, valid_window=1):  # allow 1 step before/after
        user.email_verified = True
        db.commit()
        return {"message": "Email verified successfully"}
   
    raise HTTPException(status_code=400, detail="Invalid verification code")