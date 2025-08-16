import os
from dotenv import load_dotenv
import httpx
import base64
from datetime import datetime

load_dotenv()

MPESA_ENV = os.getenv("MPESA_ENV", "sandbox")  # or "production"
MPESA_BASE_URL = "https://sandbox.safaricom.co.ke" if MPESA_ENV == "sandbox" else "https://api.safaricom.co.ke"

CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
SHORTCODE = os.getenv("MPESA_SHORTCODE")
PASSKEY = os.getenv("MPESA_PASSKEY")
CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL", "https://yourdomain.com/api/mpesa/callback")

# Step 1: Get Access Token
async def get_access_token():
    async with httpx.AsyncClient() as client:
        auth = (CONSUMER_KEY, CONSUMER_SECRET)
        response = await client.get(f"{MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials", auth=auth)
        response.raise_for_status()
        return response.json()["access_token"]

# Step 2: Initiate STK Push (C2B)
async def initiate_stk_push(phone: str, amount: float, account_ref="Chama Contribution"):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode((SHORTCODE + PASSKEY + timestamp).encode()).decode()
    
    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": account_ref,
        "TransactionDesc": "Chama Payment"
    }

    token = await get_access_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
