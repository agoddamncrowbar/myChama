from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CreateChamaRequest(BaseModel):
    name: str
    description: str = ""
    guidelines: str = ""
    monthly_contribution: float
    is_open_to_join: bool = False
    requires_approval: bool = False
    join_code: Optional[str] = None

class JoinChamaRequest(BaseModel):
    chama_id: int
    role: str
    join_code: Optional[str] = None
    
class CreateMeetingRequest(BaseModel):
    meeting_date: datetime
    location: str
    agenda: Optional[str] = None

class MemberResponse(BaseModel):
    member_id: int
    user_id: int
    full_name: str
    email: str
    phone_number: Optional[str]
    role: str
    join_date: datetime

    class Config:
        orm_mode = True

class UpdateMemberRoleRequest(BaseModel):
    new_role: str

class BulkUpdateMemberRoleItem(BaseModel):
    member_id: int
    new_role: str

class BulkUpdateMemberRolesRequest(BaseModel):
    updates: List[BulkUpdateMemberRoleItem]