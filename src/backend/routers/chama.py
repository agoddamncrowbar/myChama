from fastapi import APIRouter, Depends, HTTPException, Header, Body
from sqlalchemy.orm import Session
from jose.exceptions import ExpiredSignatureError
from database import get_db
from datetime import datetime
from models import Chama, ChamaMember, RoleEnum, JoinRequest, User, Meeting
from schemas.chama import CreateChamaRequest, JoinChamaRequest, CreateMeetingRequest, MemberResponse, UpdateMemberRoleRequest, BulkUpdateMemberRoleItem, BulkUpdateMemberRolesRequest
from auth import decode_access_token

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

@router.post("/create-chama")
def create_chama(data: CreateChamaRequest, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    new_chama = Chama(
        name=data.name,
        description=data.description,
        guidelines=data.guidelines,
        monthly_contribution=data.monthly_contribution,
        is_open_to_join=data.is_open_to_join,
        requires_approval=data.requires_approval,
        join_code=data.join_code
    )

    db.add(new_chama)
    db.commit()
    db.refresh(new_chama)

    new_member = ChamaMember(
        chama_id=new_chama.chama_id,
        user_id=user_id,
        role=RoleEnum.admin
    )
    db.add(new_member)
    db.commit()
    return {"message": "Chama created", "chama_id": new_chama.chama_id}

@router.post("/join-chama")
def join_chama(data: JoinChamaRequest, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    chama = db.query(Chama).filter(Chama.chama_id == data.chama_id).first()
    if not chama:
        raise HTTPException(404, detail="Chama not found")

    already_member = db.query(ChamaMember).filter_by(chama_id=data.chama_id, user_id=user_id).first()
    if already_member:
        raise HTTPException(400, detail="Already a member")

    if chama.is_open_to_join:
        pass
    elif chama.join_code and data.join_code == chama.join_code:
        pass
    elif chama.requires_approval:
        existing_request = db.query(JoinRequest).filter_by(user_id=user_id, chama_id=chama.chama_id, status="pending").first()
        if existing_request:
            raise HTTPException(400, detail="Join request already submitted and pending approval.")

        join_request = JoinRequest(
            user_id=user_id,
            chama_id=chama.chama_id,
            status="pending"
        )
        db.add(join_request)
        db.commit()
        return {"message": "Join request submitted and awaiting approval."}
    else:
        raise HTTPException(403, detail="You cannot join this chama without permission or a valid code.")

    member = ChamaMember(chama_id=data.chama_id, user_id=user_id, role=data.role)
    db.add(member)
    db.commit()
    return {"message": "Successfully joined chama"}

@router.get("/chamas/{chama_id}/join-requests")
def get_join_requests(chama_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    # Ensure requester is an admin of this chama
    admin = db.query(ChamaMember).filter_by(chama_id=chama_id, user_id=user_id).first()
    if not admin or admin.role not in [RoleEnum.admin,  RoleEnum.secretary, RoleEnum.treasurer]:
        raise HTTPException(403, detail="Not authorized")

    requests = (
        db.query(JoinRequest, User.full_name, User.email)
        .join(User, JoinRequest.user_id == User.user_id)
        .filter(JoinRequest.chama_id == chama_id, JoinRequest.status == "pending")
        .all()
    )
    return [
        {
            "request_id": req.JoinRequest.request_id,
            "user_id": req.JoinRequest.user_id,
            "full_name": req.full_name,
            "email": req.email,
            "requested_at": req.JoinRequest.requested_at,
            "status": req.JoinRequest.status
        }
        for req in requests
    ]

@router.post("/join-requests/{request_id}/approve")
def approve_request(request_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    join_request = db.query(JoinRequest).filter_by(request_id=request_id).first()
    if not join_request or join_request.status != "pending":
        raise HTTPException(404, detail="Join request not found or already handled")

    # Check if approver is admin of this chama
    admin = db.query(ChamaMember).filter_by(chama_id=join_request.chama_id, user_id=user_id).first()
    if not admin or admin.role not in [RoleEnum.admin, RoleEnum.secretary, RoleEnum.treasurer]:
        raise HTTPException(403, detail="Not authorized")

    # Approve → add as member
    new_member = ChamaMember(
        chama_id=join_request.chama_id,
        user_id=join_request.user_id,
        role=RoleEnum.member
    )
    db.add(new_member)
    join_request.status = "approved"
    db.commit()

    return {"message": "Request approved successfully"}

@router.post("/join-requests/{request_id}/reject")
def reject_request(request_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    join_request = db.query(JoinRequest).filter_by(request_id=request_id).first()
    if not join_request or join_request.status != "pending":
        raise HTTPException(404, detail="Join request not found or already handled")

    # Check if approver is admin
    admin = db.query(ChamaMember).filter_by(chama_id=join_request.chama_id, user_id=user_id).first()
    if not admin or admin.role not in [RoleEnum.admin, RoleEnum.chairman, RoleEnum.secretary, RoleEnum.treasurer]:
        raise HTTPException(403, detail="Not authorized")

    join_request.status = "rejected"
    db.commit()

    return {"message": "Request rejected"}

@router.post("/chamas/{chama_id}/meetings")
def create_meeting(
    chama_id: int,
    data: CreateMeetingRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    # Check if user is secretary or admin
    member = db.query(ChamaMember).filter_by(chama_id=chama_id, user_id=user_id).first()
    if not member or member.role not in [RoleEnum.admin, RoleEnum.secretary]:
        raise HTTPException(403, detail="Not authorized to schedule meetings")

    new_meeting = Meeting(
        chama_id=chama_id,
        meeting_date=data.meeting_date,
        location=data.location,
        agenda=data.agenda
    )
    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)

    return {
        "message": "Meeting scheduled",
        "meeting_id": new_meeting.meeting_id,
        "meeting_date": new_meeting.meeting_date,
        "location": new_meeting.location,
        "agenda": new_meeting.agenda,
    }

@router.get("/chamas/{chama_id}/meetings/upcoming")
def get_upcoming_meetings(
    chama_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    now = datetime.utcnow()
    meetings = (
        db.query(Meeting)
        .filter(Meeting.chama_id == chama_id, Meeting.meeting_date >= now)
        .order_by(Meeting.meeting_date.asc())
        .all()
    )

    return [
        {
            "meeting_id": m.meeting_id,
            "meeting_date": m.meeting_date,
            "location": m.location,
            "agenda": m.agenda,
        }
        for m in meetings
    ]

@router.get("/chamas/{chama_id}/meetings/previous")
def get_previous_meetings(
    chama_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    now = datetime.utcnow()
    meetings = (
        db.query(Meeting)
        .filter(Meeting.chama_id == chama_id, Meeting.meeting_date < now)
        .order_by(Meeting.meeting_date.desc())
        .all()
    )
    return [
        {
            "meeting_id": m.meeting_id,
            "meeting_date": m.meeting_date,
            "location": m.location,
            "agenda": m.agenda,
            "minutes": m.minutes,
        }
        for m in meetings
    ]

# Add or edit minutes (only secretary or admin)
@router.put("/chamas/{chama_id}/meetings/{meeting_id}/minutes")
def update_meeting_minutes(
    chama_id: int,
    meeting_id: int,
    minutes: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    member = db.query(ChamaMember).filter_by(chama_id=chama_id, user_id=user_id).first()
    if not member or member.role not in [RoleEnum.admin, RoleEnum.secretary]:
        raise HTTPException(403, detail="Not authorized to add/edit minutes")

    meeting = db.query(Meeting).filter_by(meeting_id=meeting_id, chama_id=chama_id).first()
    if not meeting:
        raise HTTPException(404, detail="Meeting not found")

    meeting.minutes = minutes
    db.commit()
    return {"message": "Minutes updated successfully", "meeting_id": meeting.meeting_id}

@router.get("/chamas/{chama_id}/members", response_model=list[MemberResponse])
def list_members(
    chama_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    # Check admin
    admin = db.query(ChamaMember).filter_by(chama_id=chama_id, user_id=user_id).first()
    if not admin or admin.role != RoleEnum.admin:
        raise HTTPException(403, detail="Only admin can view members")

    members = (
        db.query(ChamaMember, User.full_name, User.email, User.phone_number)
        .join(User, ChamaMember.user_id == User.user_id)
        .filter(ChamaMember.chama_id == chama_id)
        .all()
    )

    return [
        MemberResponse(
            member_id=m.ChamaMember.member_id,
            user_id=m.ChamaMember.user_id,
            full_name=m.full_name,
            email=m.email,
            phone_number=m.phone_number,
            role=m.ChamaMember.role.value,
            join_date=m.ChamaMember.join_date,
        )
        for m in members
    ]


@router.put("/chamas/{chama_id}/members/{member_id}/role")
def update_member_role(
    chama_id: int,
    member_id: int,
    data: UpdateMemberRoleRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    # Check admin
    admin = db.query(ChamaMember).filter_by(chama_id=chama_id, user_id=user_id).first()
    if not admin or admin.role != RoleEnum.admin:
        raise HTTPException(403, detail="Only admin can update member roles")

    member = db.query(ChamaMember).filter_by(chama_id=chama_id, member_id=member_id).first()
    if not member:
        raise HTTPException(404, detail="Member not found in this chama")

    if member.role == RoleEnum.admin:
        raise HTTPException(400, detail="Cannot change role of another admin")

    member.role = RoleEnum(data.new_role)
    db.commit()

    return {"message": "Member role updated", "member_id": member.member_id, "new_role": member.role.value}


@router.delete("/chamas/{chama_id}/members/{member_id}")
def remove_member(
    chama_id: int,
    member_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    # Check admin
    admin = db.query(ChamaMember).filter_by(chama_id=chama_id, user_id=user_id).first()
    if not admin or admin.role != RoleEnum.admin:
        raise HTTPException(403, detail="Only admin can remove members")

    member = db.query(ChamaMember).filter_by(chama_id=chama_id, member_id=member_id).first()
    if not member:
        raise HTTPException(404, detail="Member not found in this chama")

    if member.role == RoleEnum.admin:
        raise HTTPException(400, detail="Cannot remove another admin")

    db.delete(member)
    db.commit()

    return {"message": "Member removed successfully", "member_id": member_id}

@router.put("/chamas/{chama_id}/update-roles")
def bulk_update_roles(
    chama_id: int,
    request: BulkUpdateMemberRolesRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    # Ensure the current user is an admin
    admin = db.query(ChamaMember).filter_by(chama_id=chama_id, user_id=user_id).first()
    if not admin or admin.role != RoleEnum.admin:
        raise HTTPException(403, detail="Only admin can update member roles")

    updated_members = []
    for update in request.updates:
        member = db.query(ChamaMember).filter_by(chama_id=chama_id, member_id=update.member_id).first()
        if not member:
            continue
        if member.role == RoleEnum.admin:
            continue  # prevent demoting other admins

        member.role = RoleEnum(update.new_role)
        updated_members.append({"member_id": member.member_id, "new_role": member.role.value})

    db.commit()

    return {"message": "Roles updated successfully", "updated": updated_members}
