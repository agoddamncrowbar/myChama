import base64
from datetime import datetime
import requests
from dotenv import load_dotenv
import os
from fastapi import HTTPException

load_dotenv()

class MpesaService:
    def __init__(self):
        self.env = os.getenv("MPESA_ENV", "sandbox")
        self.base_url = (
            "https://sandbox.safaricom.co.ke" 
            if self.env == "sandbox" 
            else "https://api.safaricom.co.ke"
        )
        self.consumer_key = os.getenv("MPESA_CONSUMER_KEY")
        self.consumer_secret = os.getenv("MPESA_CONSUMER_SECRET")
        self.passkey = os.getenv("MPESA_PASSKEY")
        self.business_shortcode = os.getenv("MPESA_BUSINESS_SHORTCODE")
        self.callback_url = os.getenv("MPESA_CALLBACK_URL")
        self.access_token = self._get_access_token()

    def _get_access_token(self):
        auth_string = f"{self.consumer_key}:{self.consumer_secret}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_auth}"
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials",
                headers=headers
            )
            response.raise_for_status()
            return response.json()["access_token"]
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get M-Pesa access token: {str(e)}"
            )

    def initiate_stk_push(self, phone_number: str, amount: int, reference: str, description: str):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(
            f"{self.business_shortcode}{self.passkey}{timestamp}".encode()
        ).decode()
        
        payload = {
            "BusinessShortCode": self.business_shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": self.business_shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": self.callback_url,
            "AccountReference": reference,
            "TransactionDesc": description
        }
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/mpesa/stkpush/v1/processrequest",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"STK push failed: {str(e)}"
            )