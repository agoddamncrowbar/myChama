import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
import asyncpg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/mychama")

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# M-Pesa configuration
MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
MPESA_BUSINESS_SHORTCODE = os.getenv("MPESA_BUSINESS_SHORTCODE")
MPESA_PASSKEY = os.getenv("MPESA_PASSKEY")

# Initialize FastAPI app
app = FastAPI(title="MyChama API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security utilities
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
class UserBase(BaseModel):
    phone_number: str
    email: Optional[str] = None
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: int
    hashed_password: str
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    phone_number: Optional[str] = None

class ChamaBase(BaseModel):
    name: str
    description: str
    monthly_contribution: float

class ChamaCreate(ChamaBase):
    pass

class ChamaInDB(ChamaBase):
    id: int
    created_at: datetime
    creator_id: int

class MpesaLoginRequest(BaseModel):
    phone_number: str

# Database connection pool
async def get_db():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()

# Authentication utilities
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def get_user(conn, phone_number: str):
    user = await conn.fetchrow(
        "SELECT * FROM users WHERE phone_number = $1", phone_number
    )
    if user:
        return UserInDB(**user)

async def authenticate_user(conn, phone_number: str, password: str):
    user = await get_user(conn, phone_number)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    conn = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone_number: str = payload.get("sub")
        if phone_number is None:
            raise credentials_exception
        token_data = TokenData(phone_number=phone_number)
    except JWTError:
        raise credentials_exception
    
    user = await get_user(conn, phone_number=token_data.phone_number)
    if user is None:
        raise credentials_exception
    return user

# M-Pesa service
class MpesaService:
    def __init__(self):
        self.base_url = "https://sandbox.safaricom.co.ke"  # Use production URL in prod
        self.access_token = self._get_access_token()

    def _get_access_token(self):
        auth_string = f"{MPESA_CONSUMER_KEY}:{MPESA_CONSUMER_SECRET}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        headers = {"Authorization": f"Basic {encoded_auth}"}
        
        response = requests.get(
            f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials",
            headers=headers
        )
        response.raise_for_status()
        return response.json()["access_token"]

    async def stk_push(self, phone_number: str, amount: int, reference: str, description: str):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(
            f"{MPESA_BUSINESS_SHORTCODE}{MPESA_PASSKEY}{timestamp}".encode()
        ).decode()
        
        payload = {
            "BusinessShortCode": MPESA_BUSINESS_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": MPESA_BUSINESS_SHORTCODE,
            "PhoneNumber": phone_number,
            "CallBackURL": f"{os.getenv('BASE_URL')}/api/mpesa/callback",
            "AccountReference": reference,
            "TransactionDesc": description
        }
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{self.base_url}/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        return response.json()

# API endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    conn = Depends(get_db)
):
    user = await authenticate_user(conn, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.phone_number}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=UserInDB)
async def create_user(user: UserCreate, conn = Depends(get_db)):
    # Check if user already exists
    existing_user = await conn.fetchrow(
        "SELECT 1 FROM users WHERE phone_number = $1 OR email = $2",
        user.phone_number, user.email
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this phone number or email already exists"
        )
    
    hashed_password = get_password_hash(user.password)
    db_user = await conn.fetchrow(
        """INSERT INTO users (phone_number, email, full_name, hashed_password)
           VALUES ($1, $2, $3, $4) RETURNING id, phone_number, email, full_name, hashed_password, is_active""",
        user.phone_number, user.email, user.full_name, hashed_password
    )
    return UserInDB(**db_user)

@app.get("/users/me/", response_model=UserInDB)
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    return current_user

@app.post("/chamas/", response_model=ChamaInDB)
async def create_chama(
    chama: ChamaCreate,
    current_user: UserInDB = Depends(get_current_user),
    conn = Depends(get_db)
):
    # Start transaction
    async with conn.transaction():
        # Create chama
        db_chama = await conn.fetchrow(
            """INSERT INTO chamas (name, description, monthly_contribution, creator_id)
               VALUES ($1, $2, $3, $4)
               RETURNING id, name, description, monthly_contribution, created_at, creator_id""",
            chama.name, chama.description, chama.monthly_contribution, current_user.id
        )
        
        # Add creator as admin member
        await conn.execute(
            """INSERT INTO chama_members (chama_id, user_id, role)
               VALUES ($1, $2, 'admin')""",
            db_chama["id"], current_user.id
        )
        
        return ChamaInDB(**db_chama)

@app.post("/auth/mpesa/login/initiate")
async def initiate_mpesa_login(
    request: MpesaLoginRequest,
    conn = Depends(get_db)
):
    # Validate phone number format
    if not request.phone_number.startswith("254") or len(request.phone_number) != 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number must be in 254XXXXXXXXX format"
        )
    
    # Check if user exists
    user = await get_user(conn, request.phone_number)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Generate unique reference
    request_id = str(uuid.uuid4())
    
    # Initiate STK push for 1 KSH
    mpesa = MpesaService()
    try:
        response = await mpesa.stk_push(
            phone_number=request.phone_number,
            amount=1,
            reference=f"LOGIN_{request_id[:8]}",
            description="MyChama login verification"
        )
        
        # Store the login request (in production, use a database)
        login_requests[request_id] = {
            "phone_number": request.phone_number,
            "merchant_request_id": response.get("MerchantRequestID"),
            "status": "pending",
            "created_at": datetime.utcnow()
        }
        
        return {
            "request_id": request_id,
            "message": "M-Pesa payment request sent to your phone"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/mpesa/callback")
async def mpesa_callback(request: Request):
    data = await request.json()
    callback = data.get("Body", {}).get("stkCallback", {})
    
    if callback.get("ResultCode") == "0":
        # Successful payment
        merchant_request_id = callback["MerchantRequestID"]
        items = callback.get("CallbackMetadata", {}).get("Item", [])
        
        payment_data = {
            "amount": next((item["Value"] for item in items if item["Name"] == "Amount"), None),
            "mpesa_receipt": next((item["Value"] for item in items if item["Name"] == "MpesaReceiptNumber"), None),
            "phone_number": next((item["Value"] for item in items if item["Name"] == "PhoneNumber"), None),
            "transaction_date": next((item["Value"] for item in items if item["Name"] == "TransactionDate"), None),
        }
        
        # Find matching login request
        for request_id, request in login_requests.items():
            if request.get("merchant_request_id") == merchant_request_id:
                request["status"] = "success"
                request["payment_data"] = payment_data
                break
        
        return {"status": "success"}
    else:
        error_message = callback.get("ResultDesc", "Payment failed")
        return {"status": "failed", "reason": error_message}

# Serve frontend in production
if os.getenv("PRODUCTION") == "true":
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)