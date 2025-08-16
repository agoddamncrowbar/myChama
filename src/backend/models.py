from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, DECIMAL, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from sqlalchemy import Enum as PgEnum
from enum import Enum

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    id_scan_url = Column(String(255), nullable=True)
    verified = Column(Boolean, default=False)
    alternate_phone_number = Column(String(20), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    profile_picture_url = Column(String(255), nullable=True)
    email_verified = Column(Boolean, default=False)
    email_verification_secret = Column(String(32), nullable=True)
    # Relationships
    chama_memberships = relationship("ChamaMember", back_populates="user")

class Chama(Base):
    __tablename__ = "chamas"

    chama_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    guidelines = Column(String(255), nullable=True)
    monthly_contribution = Column(Float, nullable=False)
    is_open_to_join = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=False)         
    join_code = Column(String(10), nullable=True, unique=True)
    # Relationships
    members = relationship("ChamaMember", back_populates="chama")
    contributions = relationship("Contribution", back_populates="chama")
    loans = relationship("Loan", back_populates="chama")
    meetings = relationship("Meeting", back_populates="chama")

class JoinRequest(Base):
    __tablename__ = "join_requests"

    request_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    chama_id = Column(Integer, ForeignKey("chamas.chama_id"))
    status = Column(String(20), default="pending") 
    requested_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("User")
    chama = relationship("Chama")


class RoleEnum(str, Enum):
    admin = "admin"
    secretary = "secretary"
    treasurer = "treasurer"
    member = "member"

class ChamaMember(Base):
    __tablename__ = "chama_members"

    member_id = Column(Integer, primary_key=True)
    chama_id = Column(Integer, ForeignKey("chamas.chama_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    role = Column(PgEnum(RoleEnum, name="role_enum", create_type=True), nullable=False)

    join_date = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    chama = relationship("Chama", back_populates="members")
    user = relationship("User", back_populates="chama_memberships")
    contributions = relationship("Contribution", back_populates="member")
    loans = relationship("Loan", back_populates="member")

class Contribution(Base):
    __tablename__ = "contributions"

    contribution_id = Column(Integer, primary_key=True)
    chama_id = Column(Integer, ForeignKey("chamas.chama_id"))
    member_id = Column(Integer, ForeignKey("chama_members.member_id"))
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_date = Column(TIMESTAMP, default=datetime.utcnow)
    mpesa_code = Column(String(50), unique=True)
    verified = Column(Boolean, default=False)

    # Relationships
    chama = relationship("Chama", back_populates="contributions")
    member = relationship("ChamaMember", back_populates="contributions")

class Loan(Base):
    __tablename__ = "loans"

    loan_id = Column(Integer, primary_key=True)
    chama_id = Column(Integer, ForeignKey("chamas.chama_id"))
    member_id = Column(Integer, ForeignKey("chama_members.member_id"))
    amount = Column(DECIMAL(10, 2), nullable=False)
    interest_rate = Column(DECIMAL(5, 2), default=0.0)
    disbursement_date = Column(TIMESTAMP, nullable=True)
    due_date = Column(TIMESTAMP, nullable=True)
    status = Column(String(20), default="pending")
    purpose = Column(Text)

    # Relationships
    chama = relationship("Chama", back_populates="loans")
    member = relationship("ChamaMember", back_populates="loans")
    payments = relationship("LoanPayment", back_populates="loan")

class LoanPayment(Base):
    __tablename__ = "loan_payments"

    payment_id = Column(Integer, primary_key=True)
    loan_id = Column(Integer, ForeignKey("loans.loan_id"))
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_date = Column(TIMESTAMP, default=datetime.utcnow)
    mpesa_code = Column(String(50), unique=True)

    # Relationships
    loan = relationship("Loan", back_populates="payments")

class Meeting(Base):
    __tablename__ = "meetings"

    meeting_id = Column(Integer, primary_key=True)
    chama_id = Column(Integer, ForeignKey("chamas.chama_id"))
    meeting_date = Column(TIMESTAMP, nullable=False)
    location = Column(String(255))
    agenda = Column(Text)
    minutes = Column(Text)

    # Relationships
    chama = relationship("Chama", back_populates="meetings")
