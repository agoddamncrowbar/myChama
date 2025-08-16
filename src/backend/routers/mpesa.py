from fastapi import APIRouter, Depends, HTTPException, Request
from services.mpesa import initiate_stk_push
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from database import get_db
from models import User

router = APIRouter()

class PaymentRequest(BaseModel):
    phone: str
    amount: float
    chama_id: int

@router.post("/mpesa/pay")
async def make_payment(data: PaymentRequest, db: Session = Depends(get_db)):
    # Optional: Validate chama and user membership

    try:
        result = await initiate_stk_push(data.phone, data.amount)
        return {"success": True, "response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mpesa/callback")
async def mpesa_callback(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    print("M-PESA Callback:", body)
    # Optionally: Parse body and store transaction in your DB
    return {"status": "received"}