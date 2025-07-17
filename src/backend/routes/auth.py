from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import uuid
import time
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional

from services.mpesa import MpesaService
from models import LoginRequest, User

router = APIRouter(prefix="/auth", tags=["authentication"])

# Configuration (move to settings.py in production)
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# In-memory storage (use Redis/DB in production)
login_requests = {}
mpesa_transactions = {}

class MpesaLoginRequest(BaseModel):
    phone_number: str

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/mpesa/login/initiate", response_model=dict)
async def initiate_mpesa_login(request: MpesaLoginRequest):
    # Validate phone number format (254XXXXXXXXX)
    if not request.phone_number.startswith("254") or len(request.phone_number) != 12:
        raise HTTPException(
            status_code=400,
            detail="Phone number must be in 254XXXXXXXXX format"
        )

    # Generate unique request ID
    request_id = str(uuid.uuid4())
    
    # Store the login request
    login_requests[request_id] = {
        "phone_number": request.phone_number,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(minutes=5)
    }
    
    # Initiate STK push for 1 KSH
    mpesa = MpesaService()
    try:
        response = mpesa.initiate_stk_push(
            phone_number=request.phone_number,
            amount=1,
            reference=f"LOGIN_{request_id[:8]}",
            description="MyChama login verification"
        )
        
        # Save merchant request ID for callback matching
        login_requests[request_id]["merchant_request_id"] = response.get("MerchantRequestID")
        
        return {
            "request_id": request_id,
            "message": "M-Pesa payment request sent to your phone",
            "expires_in": 300  # 5 minutes
        }
    except HTTPException as e:
        login_requests[request_id]["status"] = "failed"
        raise e

@router.get("/mpesa/login/status/{request_id}", response_model=Token)
async def check_login_status(request_id: str):
    # Check if request exists
    if request_id not in login_requests:
        raise HTTPException(status_code=404, detail="Login request not found")
    
    request_data = login_requests[request_id]
    
    # Check if expired
    if datetime.utcnow() > request_data["expires_at"]:
        login_requests[request_id]["status"] = "expired"
        raise HTTPException(status_code=400, detail="Login request expired")
    
    # Check if payment was received
    if request_data["status"] == "success":
        # Get user by phone number (implement your own user lookup)
        user = await get_user_by_phone(request_data["phone_number"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.phone_number},
            expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    # Still pending
    return {"status": "pending", "message": "Waiting for payment confirmation"}

@router.post("/mpesa/callback")
async def mpesa_callback(data: dict):
    try:
        callback = data.get("Body", {}).get("stkCallback", {})
        
        if callback.get("ResultCode") == "0":
            # Successful payment
            merchant_request_id = callback["MerchantRequestID"]
            callback_metadata = callback["CallbackMetadata"]["Item"]
            
            # Extract payment details
            payment_data = {
                "amount": next(item["Value"] for item in callback_metadata if item["Name"] == "Amount"),
                "mpesa_receipt_number": next(item["Value"] for item in callback_metadata if item["Name"] == "MpesaReceiptNumber"),
                "phone_number": next(item["Value"] for item in callback_metadata if item["Name"] == "PhoneNumber"),
                "transaction_date": next(item["Value"] for item in callback_metadata if item["Name"] == "TransactionDate"),
            }
            
            # Find matching login request
            for request_id, request in login_requests.items():
                if request.get("merchant_request_id") == merchant_request_id:
                    # Update request status
                    request["status"] = "success"
                    request["payment_data"] = payment_data
                    
                    # Store transaction details
                    mpesa_transactions[payment_data["mpesa_receipt_number"]] = {
                        "request_id": request_id,
                        "phone_number": payment_data["phone_number"],
                        "amount": payment_data["amount"],
                        "timestamp": datetime.utcnow()
                    }
                    
                    return {"status": "success"}
            
            return {"status": "failed", "reason": "No matching login request found"}
        else:
            error_message = callback.get("ResultDesc", "Payment failed")
            return {"status": "failed", "reason": error_message}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def get_user_by_phone(phone_number: str):
    """
    Replace this with your actual user lookup logic
    """
    # Example: query your database
    # return await User.get(phone_number=phone_number)
    return {"phone_number": phone_number, "user_id": "123"}  # Mock response