from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import enum

class UserStatus(enum.Enum):
    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    DELETED = "deleted"

class UserRole(enum.Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String(255), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING_VERIFICATION, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    photos = relationship("UserPhoto", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sent_matches = relationship("Match", foreign_keys="[Match.sender_id]", back_populates="sender", cascade="all, delete-orphan")
    received_matches = relationship("Match", foreign_keys="[Match.receiver_id]", back_populates="receiver", cascade="all, delete-orphan")
    sent_conversations = relationship("Conversation", foreign_keys="[Conversation.user1_id]", back_populates="user1", cascade="all, delete-orphan")
    received_conversations = relationship("Conversation", foreign_keys="[Conversation.user2_id]", back_populates="user2", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="sender", cascade="all, delete-orphan")
    charters = relationship("UserCharter", back_populates="user", cascade="all, delete-orphan")
    reports_made = relationship("Report", foreign_keys="[Report.reporter_id]", back_populates="reporter")
    reports_received = relationship("Report", foreign_keys="[Report.reported_user_id]", back_populates="reported_user")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', status='{self.status.value}')>"