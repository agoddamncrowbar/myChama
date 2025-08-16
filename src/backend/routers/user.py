from fastapi import (
    APIRouter, Depends, HTTPException, Header,
    UploadFile, File, Form
)
from sqlalchemy.orm import Session
from database import get_db
from models import Chama, ChamaMember, User
from auth import get_current_user, decode_access_token
from jose.exceptions import ExpiredSignatureError
import os, shutil
from uuid import uuid4

router = APIRouter()

def get_current_user_id(authorization: str = Header(...)) -> int:
    token = authorization.replace("Bearer ", "")
    try:
        payload = decode_access_token(token)
        return payload["user_id"]
    except ExpiredSignatureError:
        raise HTTPException(401, detail="Token has expired")
    except:
        raise HTTPException(401, detail="Invalid or expired token")

@router.get("/user-chamas")
def get_user_chamas(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]

    memberships = db.query(ChamaMember).filter_by(user_id=user_id).all()
    return [{
        "chama_id": m.chama_id,
        "name": m.chama.name,
        "role": m.role,
        "joined_on": m.join_date
    } for m in memberships]

@router.get("/my-chamas")
def get_my_chamas(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    memberships = (
        db.query(ChamaMember)
        .join(Chama)
        .filter(ChamaMember.user_id == user_id)
        .all()
    )
    return [{
        "chama_id": m.chama.chama_id,
        "name": m.chama.name,
        "description": m.chama.description,
        "role": m.role
    } for m in memberships]

@router.put("/profile")
def update_profile(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    phone_number: str = Form(None),
    alternate_phone_number: str = Form(None),
    file: UploadFile = File(None)
):
    user = db.query(User).get(user_id)

    if not user:
        raise HTTPException(404, detail="User not found")

    if phone_number:
        user.phone_number = phone_number
    if alternate_phone_number:
        user.alternate_phone_number = alternate_phone_number
    if file:
        extension = file.filename.split(".")[-1]
        filename = f"{uuid4()}.{extension}"
        filepath = f"static/profile_pics/{filename}"
        os.makedirs("static/profile_pics", exist_ok=True)

        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Save full static path (with leading slash)
        user.profile_picture_url = f"/static/profile_pics/{filename}"

    db.commit()           
    db.refresh(user)      

    return {"message": "Profile updated"} 


@router.get("/profile")
def get_user_profile(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "full_name": user.full_name,
        "email": user.email,
        "email_verified": user.email_verified,
        "phone_number": user.phone_number,
        "alternate_phone_number": user.alternate_phone_number,
        # already full URL path
        "profile_picture_url": user.profile_picture_url,
    }

